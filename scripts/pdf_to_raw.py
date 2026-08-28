#!/usr/bin/env python3
"""One-time prep: convert MOJi 考前对策 vocab PDFs -> data/raw/*.md (pipe tables).

Each PDF is a 7-column table: 序号|发音|音调|单词|词性|释义|例句. pdfplumber keeps
the columns; cells may wrap across lines, so we collapse newlines into one physical
line (parse_moji.py reads one entry per line). Output feeds parse_moji.py.

Usage:
  python3 scripts/pdf_to_raw.py \
      "N1_1-1000.pdf:n1_1_1000" \
      "N1_1001-2000.pdf:n1_1001_2000" \
      "N2_1-1000.pdf:n2_1_1000"
"""
import sys, os, re
import pdfplumber

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

def cell(s):
    if not s:
        return ""
    # collapse internal newlines/soft-wraps; CJK needs no join space
    s = s.replace("\n", "").replace("\r", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("|", "｜")

def convert(pdf_path, name):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for tbl in page.extract_tables() or []:
                for r in tbl:
                    r = list(r) + [""] * (7 - len(r)) if len(r) < 7 else r[:7]
                    seq = cell(r[0])
                    if seq in ("序号", "") or not seq.isdigit():
                        continue
                    cells = [cell(c) for c in r]
                    rows.append("|" + "|".join(cells) + "|")
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, name + ".md")
    header = ("|序号|发音|音调|单词|词性|释义|例句|\n"
              "|---|---|---|---|---|---|---|\n")
    with open(out, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(rows) + "\n")
    print(f"{name}: {len(rows)} rows -> {out}")

def main():
    for arg in sys.argv[1:]:
        pdf_path, name = arg.rsplit(":", 1)
        convert(pdf_path, name)

if __name__ == "__main__":
    main()
