#!/usr/bin/env python3
"""Tokenize ASR output, recover lemma+reading, match against MOJi headwords.

Usage:
  python3 match_moji.py asr_full.json vocab_full_hits.json \
      --moji data/moji_n1.json data/moji_n2.json --min-conf 0.6

Output: [{word(lemma), reading, level, moji, time, mmss, conf, count, sentence}]
sorted by time, one entry per matched lemma (first occurrence).
"""
import sys, json, argparse, re
import fugashi

tagger = fugashi.Tagger()

def hira(s):
    return "".join(chr(ord(c) - 0x60) if 0x30A1 <= ord(c) <= 0x30F6 else c for c in s)

def mmss(t):
    return f"{int(t)//60:02d}:{int(t)%60:02d}"

def load_moji(paths):
    """Return dict: headword -> full meta, and reading -> (headword,meta) kana fallback."""
    by_word, by_reading = {}, {}
    for p in paths:
        data = json.load(open(p, encoding="utf-8"))
        for w, meta in data.items():
            lv = meta.get("level") or ("N1" if "n1" in p.lower() else "N2")
            m = {"moji": w, "level": lv,
                 "reading": meta.get("reading", ""), "pitch": meta.get("pitch", ""),
                 "pos": meta.get("pos", ""), "meaning": meta.get("meaning", ""),
                 "example": meta.get("example", "")}
            by_word[w] = m
            r = meta.get("reading")
            if r:
                by_reading.setdefault(hira(r), m)
    return by_word, by_reading

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("asr")
    ap.add_argument("out")
    ap.add_argument("--moji", nargs="+", required=True)
    ap.add_argument("--min-conf", type=float, default=0.6)
    a = ap.parse_args()

    by_word, by_reading = load_moji(a.moji)
    segs = json.load(open(a.asr, encoding="utf-8"))

    hits = {}  # lemma -> record
    for s in segs:
        text = s["text"]
        # 词级置信度：把 ASR word 概率按顺序对齐到 fugashi token（近似）
        wconf = [w.get("p", 0) for w in s.get("words", [])]
        wi = 0
        for tok in tagger(text):
            lemma = getattr(tok.feature, "lemma", None) or tok.surface
            lemma = lemma.split("-")[0]
            # reading
            kana = getattr(tok.feature, "kana", "") or ""
            reading = hira(kana) if kana else lemma
            conf = wconf[wi] if wi < len(wconf) else 0.0
            wi += 1

            hit = None
            if lemma in by_word:
                hit = by_word[lemma]
            elif reading in by_reading:  # kana-written headwords, e.g. まとも
                hit = by_reading[reading]
            if not hit:
                continue
            if conf < a.min_conf:
                continue
            key = lemma
            if key in hits:
                hits[key]["count"] += 1
                continue
            hits[key] = {
                "word": lemma, "reading": hit["reading"] or reading, "level": hit["level"],
                "moji": hit["moji"], "pitch": hit["pitch"], "pos": hit["pos"],
                "meaning": hit["meaning"], "example": hit["example"],
                "time": round(s["start"], 2), "mmss": mmss(s["start"]),
                "conf": round(conf, 3), "count": 1, "sentence": text.strip(),
            }

    rows = sorted(hits.values(), key=lambda x: x["time"])
    json.dump(rows, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"matched {len(rows)} words -> {a.out}")

if __name__ == "__main__":
    main()
