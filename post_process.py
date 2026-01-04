from pathlib import Path
import re

AUDIT_FILE = "audit.md"
SUMMARY_FILE = "audit_summary.md"


def summarize_audit():
    text = Path(AUDIT_FILE).read_text(encoding="utf-8")

    blocks = text.split("\n---\n")
    summary_lines = ["# Text QC Summary", ""]

    for block in blocks:
        lines = block.splitlines()

        # Find section / screenshot title
        section_title = None
        for line in lines:
            if line.lower().startswith("##"):
                section_title = line.strip()
                break
            if line.startswith("- Screenshot:"):
                section_title = f"## {line.replace('- Screenshot:', '').strip()}"
                break

        if not section_title:
            continue

        issues = []
        images = []

        for line in lines:
            # Keep error statements
            if any(
                key in line.lower()
                for key in ["error", "issue", "inconsistent", "incorrect", "misspelled"]
            ):
                issues.append(line.strip())

            # Keep existing images
            if line.strip().startswith("![](") or line.strip().startswith("!["):
                images.append(line.strip())

        if not issues:
            continue

        summary_lines.append(section_title)
        summary_lines.append("")

        for issue in issues:
            summary_lines.append(f"- {issue}")

        summary_lines.append("")

        for img in images:
            summary_lines.append(img)

        summary_lines.append("")
        summary_lines.append("---")
        summary_lines.append("")

    Path(SUMMARY_FILE).write_text(
        "\n".join(summary_lines), encoding="utf-8"
    )


if __name__ == "__main__":
    summarize_audit()
