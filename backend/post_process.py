from pathlib import Path
import re
from collections import defaultdict
import ollama
from pathlib import Path

STRUCTURED_SUMMARY_FILE = "audit_summary.md"
FORMAT_PROMPT_FILE = "prompt/format_summary.txt"
MODEL = "ministral-3"

AUDIT_FILE = "audit.md"
SUMMARY_FILE = "audit_summary.md"

# Patterns that define REAL issues
QUOTE_SHOULD_PATTERN = re.compile(
    r'"[^"]+"\s+should\s+be\s+"[^"]+"',
    re.IGNORECASE
)

NUMBERED_ISSUE_PATTERN = re.compile(
    r'^\d+\.\s+\*\*".+?"\*\*',
    re.IGNORECASE
)

GRAMMAR_PATTERN = re.compile(
    r'grammatically incorrect|cannot be read naturally|typographical error',
    re.IGNORECASE
)

def is_real_issue(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    if "no clear text errors found" in line.lower():
        return False

    return (
        QUOTE_SHOULD_PATTERN.search(line)
        or NUMBERED_ISSUE_PATTERN.search(line)
        or GRAMMAR_PATTERN.search(line)
    )

def summarize_audit():
    text = Path(AUDIT_FILE).read_text(encoding="utf-8")
    blocks = text.split("\n---\n")

    summary = ["# Text QC Summary"]

    for block in blocks:
        screenshot = None

        # Screenshot is global for the block
        for line in block.splitlines():
            if line.startswith("- Screenshot:"):
                screenshot = line.replace("- Screenshot:", "").strip()
                break

        if not screenshot:
            continue

        # ✅ ONLY care about TEXT QC AUDIT section
        if "### TEXT QC AUDIT" not in block:
            continue

        audit_part = block.split("### TEXT QC AUDIT", 1)[1]

        issues = []
        for line in audit_part.splitlines():
            line = line.strip()

            # numbered issues or bullet issues
            if line.startswith("- ") or line[:2].isdigit() and "." in line[:4]:
                issues.append(line.lstrip("- ").strip())

        if not issues:
            continue

        for issue in issues:
            summary.append(f"- **{screenshot}** — {issue}")

    Path(SUMMARY_FILE).write_text("\n".join(summary), encoding="utf-8")


def llm_format_summary():
    raw = Path(SUMMARY_FILE).read_text(encoding="utf-8")
    prompt = Path(FORMAT_PROMPT_FILE).read_text(encoding="utf-8")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": raw},
        ],
        options={
            "temperature": 0,
            "top_p": 1,
        },
    )

    formatted = response["message"]["content"].strip()
    Path(STRUCTURED_SUMMARY_FILE).write_text(formatted, encoding="utf-8")

if __name__ == "__main__":
    summarize_audit()
    llm_format_summary()
