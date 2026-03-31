from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

import markdown


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "docs" / "interview_mastery"
OUTPUT_STEM = SOURCE_DIR / "interview_mastery_complete"


def source_files() -> list[Path]:
    return sorted(
        path
        for path in SOURCE_DIR.glob("[0-9][0-9]_*.md")
        if path.is_file()
    )


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line.strip())
        if match:
            return match.group(1).strip()
    return fallback


def bump_headings(text: str) -> str:
    bumped_lines: list[str] = []
    for line in text.splitlines():
        if re.match(r"^#{1,5}\s", line):
            bumped_lines.append(f"#{line}")
        else:
            bumped_lines.append(line)
    return "\n".join(bumped_lines).strip()


def build_markdown_bundle(files: list[Path]) -> str:
    generated_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    toc_lines = []
    sections = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        title = extract_title(text, path.stem)
        toc_lines.append(f"- `{path.name}`: {title}")
        sections.append(bump_headings(text))

    header = "\n".join(
        [
            "# Interview Mastery Complete Dossier",
            "",
            f"Generated: {generated_at}",
            "",
            "This document is the combined version of every file in `docs/interview_mastery/`.",
            "",
            "## Included Sections",
            "",
            *toc_lines,
            "",
        ]
    )
    body = "\n\n---\n\n".join(sections)
    return f"{header}\n{body}\n"


def build_html(markdown_text: str) -> str:
    body = markdown.markdown(
        markdown_text,
        extensions=[
            "tables",
            "fenced_code",
            "toc",
            "sane_lists",
        ],
    )
    css = """
body {
  font-family: Calibri, Arial, sans-serif;
  margin: 36px;
  color: #1f2937;
  line-height: 1.45;
}
h1, h2, h3, h4, h5, h6 {
  color: #0f172a;
  page-break-after: avoid;
}
h1 { font-size: 28px; margin-top: 18px; }
h2 { font-size: 22px; margin-top: 22px; }
h3 { font-size: 18px; margin-top: 18px; }
p, li { font-size: 11pt; }
pre, code {
  font-family: Consolas, "Courier New", monospace;
}
pre {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 12px;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
code {
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 4px;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0 18px 0;
  font-size: 10pt;
}
th, td {
  border: 1px solid #cbd5e1;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #e2e8f0;
}
blockquote {
  border-left: 4px solid #94a3b8;
  margin: 12px 0;
  padding: 6px 12px;
  color: #475569;
  background: #f8fafc;
}
hr {
  border: none;
  border-top: 1px solid #cbd5e1;
  margin: 24px 0;
}
"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Interview Mastery Complete Dossier</title>
  <style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> None:
    files = source_files()
    if not files:
        raise SystemExit("No interview mastery markdown files found.")

    combined_markdown = build_markdown_bundle(files)
    combined_html = build_html(combined_markdown)

    OUTPUT_STEM.with_suffix(".md").write_text(combined_markdown, encoding="utf-8")
    OUTPUT_STEM.with_suffix(".html").write_text(combined_html, encoding="utf-8")

    print(f"Wrote {OUTPUT_STEM.with_suffix('.md')}")
    print(f"Wrote {OUTPUT_STEM.with_suffix('.html')}")


if __name__ == "__main__":
    main()
