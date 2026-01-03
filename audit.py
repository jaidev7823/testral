# audit.py
import base64
import json
import ollama
from pathlib import Path
from PIL import Image, ImageFilter
import re

MODEL = "ministral-3"
AUDIT_FILE = "audit.md"

AUDIT_PROMPT = Path("prompt/audit.txt").read_text(encoding="utf-8")
BLOCKER_PROMPT = Path("prompt/blocker.txt").read_text(encoding="utf-8")


def downscale_image(src_path: str, max_width: int = 960, sharpen: bool = True) -> str:
    src = Path(src_path)
    out = src.with_name(src.stem + ".png")

    img = Image.open(src).convert("RGB")
    w, h = img.size

    if w > max_width:
        scale = max_width / w
        img = img.resize((max_width, int(h * scale)), Image.LANCZOS)

    if sharpen:
        img = img.filter(
            ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3)
        )

    img.save(out, optimize=True)
    return str(out)


def extract_json(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty model output")

    text = re.sub(r"```(?:json)?", "", text, flags=re.I).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.S)
    if match:
        return json.loads(match.group(0))

    raise ValueError("No valid JSON found")


def vision_call(prompt: str, image_path: str, is_blocker: bool = False) -> dict:
    model = MODEL if not is_blocker else "ministral-3"

    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img]
        }],
        options={"temperature": 0},
        stream=False
    )

    raw = response["message"]["content"]

    try:
        return extract_json(raw)
    except Exception as e:
        print("\n[AUDIT] JSON parse failed")
        print("[AUDIT] Raw output:")
        print(raw if raw else "<EMPTY>")

        return {
            "blocker": {"suspected": False},
            "issues": [],
            "_error": str(e)
        }

def vision_call_text(prompt: str, image_path: str) -> str:
    """
    Used ONLY for blocker grounding.
    Returns raw text exactly as model outputs.
    """
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = ollama.chat(
        model="ministral-3",
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img]
        }],
        options={"temperature": 0},
        stream=False
    )

    return response["message"]["content"]

def log(title, img, payload):
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(f"## {title}\n")
        f.write(f"- Screenshot: {img}\n\n")
        f.write(json.dumps(payload, indent=2))
        f.write("\n\n---\n\n")


def run_audit(step, image, suffix="Initial"):
    print(f"[STEP {step}] Running {suffix} audit")

    ds_image = downscale_image(image)
    result = vision_call(AUDIT_PROMPT, ds_image)

    blocked = bool(result.get("blocker", {}).get("suspected", False))

    if blocked:
        log(f"Step {step} — {suffix} Blocker Detected", image, result)
        return result, True

    log(f"Step {step} — {suffix} Audit", image, result)
    return result, False


def run_blocker_audit(step, image):
    print(f"[STEP {step}] Running blocker grounding")

    ds_image = downscale_image(image)
    raw = vision_call_text(BLOCKER_PROMPT, ds_image)

    print("[BLOCKER RAW]")
    print(raw)

    idx = parse_close_number(raw)

    log(
        f"Step {step} — Blocker Grounding",
        image,
        {"raw": raw, "close_number": idx}
    )

    return idx

def parse_close_number(text: str):
    match = re.search(r"CLOSE_NUMBER:\s*(\d+)", text)
    return int(match.group(1)) if match else None
