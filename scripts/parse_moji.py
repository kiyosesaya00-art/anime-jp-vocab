#!/usr/bin/env python3
"""Parse MOJi 考前对策 vocab tables (markdown) -> data/moji_n1.json / moji_n2.json.

Reads data/raw/n1_*.md and data/raw/n2_*.md. Each data row is a single pipe line:
    序号|发音|音调|单词|词性|释义|例句
(<br> already collapsed; one entry per line).

Rules:
- skip header/separator/empty lines
- skip 惯用(idioms) / 文法(grammar) / 接头 / 接尾 / 接续 affixes and sentence-rows
  (they have no clean single headword for matching)
- reading = 发音 with spaces/full-width spaces removed
- key = 单词 (dict headword)
- 重复归 N2: any headword present in N2 is removed from N1
- level inferred from filename prefix (n1_* / n2_*)
"""
import json, glob, re, os

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT = os.path.join(os.path.dirname(__file__), "..", "data")

SKIP_POS = {"惯用", "文法", "接头", "接尾", "接续", "接続"}

def clean(s):
    return s.replace("<br>", "").replace("\u3000", "").strip()

def is_headword(word, pos):
    if not word:
        return False
    if pos in SKIP_POS:
        return False
    # 整句（含句号/多读点）或过长的短语，视为惯用句，跳过
    if "。" in word or "、" in word:
        return False
    if len(word) > 12:
        return False
    return True

def parse_file(path, level):
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        cells = [clean(c) for c in line.strip("|").split("|")]
        if len(cells) < 6:
            continue
        seq = cells[0]
        if seq in ("序号", "") or set(seq) <= set("-: "):
            continue
        reading = cells[1].replace(" ", "")
        pitch = cells[2]
        word = cells[3]
        pos = cells[4]
        meaning = cells[5] if len(cells) > 5 else ""
        example = cells[6] if len(cells) > 6 else ""
        if not is_headword(word, pos):
            continue
        out.setdefault(word, {
            "reading": reading, "pitch": pitch, "pos": pos,
            "meaning": meaning, "example": example, "level": level,
        })
    return out

def main():
    n2 = {}
    for f in sorted(glob.glob(os.path.join(RAW, "n2_*.md"))):
        n2.update(parse_file(f, "N2"))
    n1 = {}
    for f in sorted(glob.glob(os.path.join(RAW, "n1_*.md"))):
        n1.update(parse_file(f, "N1"))
    # 重复归 N2
    for w in list(n1):
        if w in n2:
            del n1[w]
    json.dump(n2, open(os.path.join(OUT, "moji_n2.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(n1, open(os.path.join(OUT, "moji_n1.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"N2 headwords: {len(n2)}")
    print(f"N1 headwords: {len(n1)} (dup->N2 removed)")

if __name__ == "__main__":
    main()
