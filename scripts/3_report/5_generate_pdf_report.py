"""
5_generate_pdf_report.py
------------------------
Converts the Markdown discrepancy report into a presentation-ready PDF
document utilizing xhtml2pdf with executive-level styling.

Reads:
    reports/differences_report_2025.md

Outputs:
    reports/differences_report_2025.pdf

Usage:
    python scripts/3_report/5_generate_pdf_report.py
"""

import os
import sys
import io
import markdown
from xhtml2pdf import pisa

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def _find_root() -> str:
    candidate = os.path.abspath(__file__)
    for _ in range(6):
        candidate = os.path.dirname(candidate)
        if os.path.isdir(os.path.join(candidate, "data")) and os.path.isdir(os.path.join(candidate, "scripts")):
            return candidate
    raise RuntimeError("Repository root directory not found.")

ROOT       = _find_root()
INPUT_MD   = os.path.join(ROOT, "reports", "differences_report_2025.md")
OUTPUT_PDF = os.path.join(ROOT, "reports", "differences_report_2025.pdf")

with open(INPUT_MD, encoding="utf-8") as f:
    md_text = f.read()

body_html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

CSS = """
@page {
    size: a4 portrait;
    margin: 2cm 1.8cm 2.2cm 1.8cm;
    @bottom-right {
        content: "Page " counter(page);
        font-size: 8pt;
        color: #888;
    }
}
body { font-family: Helvetica, Arial, sans-serif; font-size: 9pt; line-height: 1.5; color: #1a1a2e; }
h1 { font-size: 15pt; font-weight: bold; color: #1a237e; border-bottom: 2pt solid #1a237e; padding-bottom: 6pt; margin-bottom: 14pt; }
h2 { font-size: 11pt; font-weight: bold; color: #283593; background-color: #e8eaf6; padding: 5pt 5pt 5pt 10pt; margin-top: 18pt; margin-bottom: 8pt; border-left: 4pt solid #3949ab; }
h3 { font-size: 10pt; font-weight: bold; color: #1565c0; margin-top: 14pt; margin-bottom: 4pt; border-bottom: 0.5pt solid #bbdefb; padding-bottom: 2pt; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0 12pt 0; font-size: 8pt; }
th { background-color: #1a237e; color: #ffffff; padding: 5pt 7pt; text-align: left; font-weight: bold; }
td { padding: 4pt 7pt; border-bottom: 0.5pt solid #e0e0e0; vertical-align: top; }
tr:nth-child(even) td { background-color: #f5f7ff; }
tr:last-child td { background-color: #e8eaf6; font-weight: bold; }
ul { margin: 4pt 0 8pt 0; padding-left: 0; list-style: none; }
li { padding: 4pt 8pt; margin-bottom: 3pt; font-size: 8.5pt; border-left: 3pt solid #9e9e9e; background-color: #fafafa; }
hr { border-top: 0.5pt solid #e0e0e0; margin: 14pt 0 10pt 0; }
blockquote { background-color: #e8f5e9; border-left: 4pt solid #2e7d32; margin: 8pt 0; padding: 6pt 12pt; font-size: 8.5pt; color: #1b5e20; }
code { font-family: Courier, monospace; font-size: 7.5pt; background-color: #eeeeee; padding: 1pt 3pt; color: #37474f; }
strong { color: #0d1b4b; }
p { margin: 4pt 0; }
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><style>{CSS}</style></head>
<body>{body_html}</body>
</html>"""

print(f"[INFO] Generating PDF report...")
with open(OUTPUT_PDF, "wb") as pdf_file:
    status = pisa.CreatePDF(html.encode("utf-8"), dest=pdf_file, encoding="utf-8")

if status.err:
    print(f"[ERROR] PDF generation error code: {status.err}")
    sys.exit(1)

size = os.path.getsize(OUTPUT_PDF)
print(f"[SUCCESS] PDF generated: {OUTPUT_PDF} ({size/1024:.1f} KB)")
