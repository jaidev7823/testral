# audit.py
import base64
import re
import ollama
from pathlib import Path

MODEL = "qwen3-vl"
AUDIT_FILE = "audit.md"

AUDIT_PROMPT = Path("prompt/audit.txt").read_text(encoding="utf-8")
BLOCKER_PROMPT = Path("prompt/blocker.txt").read_text(encoding="utf-8")


def vision_call(prompt: str, image_path: str) -> str:
    print(f"[VISION] Analyzing image: {image_path}")

    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    res = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img]
        }],
        options={"temperature": 0}
    )
    return res["message"]["content"]


def parse_blocker(text: str) -> bool:
    blocked = bool(re.search(r"SUSPECTED:\s*YES", text, re.I))
    print(f"[AUDIT] Blocker suspected: {blocked}")
    return blocked


def parse_number(text: str):
    m = re.search(r"CLOSE_NUMBER:\s*(\d+)", text)
    idx = int(m.group(1)) if m else None
    print(f"[AUDIT] Close button index: {idx}")
    return idx


def log(title, img, text):
    print(f"[LOG] {title}")
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(f"## {title}\n")
        f.write(f"- Screenshot: {img}\n\n")
        f.write(text.strip() + "\n\n---\n\n")


def run_audit(step, image, suffix="Initial"):
    print(f"[STEP {step}] Running {suffix} audit")
    text = vision_call(AUDIT_PROMPT, image)
    blocked = parse_blocker(text)
    log(f"Step {step} — {suffix} Audit", image, text)
    return text, blocked


def run_blocker_audit(step, image):
    print(f"[STEP {step}] Running blocker grounding")
    text = vision_call(BLOCKER_PROMPT, image)
    idx = parse_number(text)
    log(f"Step {step} — Blocker Grounding", image, text)
    return idx
