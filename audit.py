# audit.py
import base64
import ollama
from pathlib import Path
from PIL import Image, ImageFilter
import re

MODEL = "devstral-small-2"
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


def vision_call(prompt: str, image_path: str) -> str:
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img]
        }],
        options={"temperature": 0},
        stream=False
    )

    return response["message"]["content"] or ""


def vision_call_text(prompt: str, image_path: str) -> str:
    """
    Used ONLY for blocker grounding.
    Returns raw text exactly as model outputs.
    """
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img]
        }],
        options={"temperature": 0},
        stream=False
    )

    return response["message"]["content"] or ""


def log(title, img, text):
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(f"## {title}\n")
        f.write(f"- Screenshot: {img}\n\n")
        f.write("```\n")
        f.write(text.strip() if text else "<EMPTY OUTPUT>")
        f.write("\n```\n\n---\n\n")


def _detect_blocker_from_text(text: str) -> bool:
    """
    Minimal heuristic.
    Adjust keywords if needed.
    """
    if not text:
        return False

    return bool(re.search(
        r"\b(cookie|consent|subscribe|sign up|modal|popup|overlay)\b",
        text,
        re.I
    ))


def run_audit(step, image, suffix="Initial"):
    print(f"[STEP {step}] Running {suffix} audit")

    ds_image = downscale_image(image)
    output = vision_call(AUDIT_PROMPT, ds_image)

    blocked = _detect_blocker_from_text(output)

    if blocked:
        log(f"Step {step} — {suffix} Blocker Detected", image, output)
        return output, True

    log(f"Step {step} — {suffix} Audit", image, output)
    return output, False


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
        raw + f"\n\n[CLOSE_NUMBER]: {idx}"
    )

    return idx

def parse_close_number(text: str):
    if not text:
        return None

    # Explicit NONE handling (valid outcome)
    if re.search(r"CLOSE_NUMBER:\s*NONE\b", text, re.I):
        return None

    # Normal numeric close
    match = re.search(r"CLOSE_NUMBER:\s*(\d+)", text)
    return int(match.group(1)) if match else None
