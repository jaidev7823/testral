# post_process.py
import json
from pathlib import Path
from PIL import Image

AUDIT_FILE = "audit.md"
OUTPUT_DIR = Path("docs")
CROP_DIR = OUTPUT_DIR / "crops"
REPORT_FILE = OUTPUT_DIR / "report.md"

OUTPUT_DIR.mkdir(exist_ok=True)
CROP_DIR.mkdir(parents=True, exist_ok=True)


def parse_audit_md():
    text = Path(AUDIT_FILE).read_text(encoding="utf-8")
    blocks = text.split("\n---\n")

    results = []

    for block in blocks:
        if "- Screenshot:" not in block:
            continue

        lines = block.splitlines()
        screenshot = None
        json_start = None

        for i, line in enumerate(lines):
            if line.startswith("- Screenshot:"):
                screenshot = line.replace("- Screenshot:", "").strip()
            if line.strip().startswith("{"):
                json_start = i
                break

        if not screenshot or json_start is None:
            continue

        payload = json.loads("\n".join(lines[json_start:]))

        issues = payload.get("issues", [])
        if issues:
            results.append({
                "screenshot": screenshot,
                "issues": issues
            })

    return results


def crop_issues(entries):
    for entry in entries:
        img = Image.open(entry["screenshot"])

        valid_issues = []

        for i, issue in enumerate(entry["issues"], 1):
            bbox = issue.get("bbox")

            if not is_valid_bbox(bbox):
                print(
                    f"[POST] Skipping invalid bbox in {entry['screenshot']}: {bbox}"
                )
                continue

            crop = img.crop(tuple(map(int, bbox)))
            out = CROP_DIR / f"{Path(entry['screenshot']).stem}_issue_{i}.png"
            crop.save(out, optimize=True)

            issue["crop"] = out.as_posix()
            valid_issues.append(issue)

        # Keep only issues that actually produced crops
        entry["issues"] = valid_issues



def generate_report(entries):
    lines = ["# Text QC Audit Report", "", "---", ""]

    for entry in entries:
        if not entry["issues"]:
            continue

        lines.append(f"## {entry['screenshot']}")
        lines.append("")

        for i, issue in enumerate(entry["issues"], 1):
            lines.extend([
                f"### {i}. \"{issue['text']}\"",
                "",
                f"**Type:** {issue['type']}",
                "",
                f"**Explanation:** {issue['explanation']}",
                "",
                f"![Issue Screenshot]({issue['crop']})",
                "",
                "---",
                ""
            ])

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

def main():
    entries = parse_audit_md()

    if not entries:
        print("[POST] No issues found.")
        return

    crop_issues(entries)
    generate_report(entries)

    print(f"[POST] Report generated → {REPORT_FILE}")

def is_valid_bbox(bbox):
    """
    Valid bbox must be:
    - list or tuple
    - length == 4
    - all values are ints
    - x2 > x1 and y2 > y1
    """
    if not isinstance(bbox, (list, tuple)):
        return False

    if len(bbox) != 4:
        return False

    try:
        x1, y1, x2, y2 = map(int, bbox)
    except Exception:
        return False

    return x2 > x1 and y2 > y1


if __name__ == "__main__":
    main()
