#!/usr/bin/env python3
"""Build the MOJi-hit vocabulary table (Markdown) from matched words + ASR hits.

Usage:
  python3 build_table.py \
      --matched data/moji_matched.json \
      --hits vocab_full_hits.json \
      --title "银魂 ep393434（01-02合集）" \
      --url https://www.bilibili.com/bangumi/play/ep393434 \
      --deepdive deepdives.md \
      --out out.md

- matched: {anime_word: {level,moji,reading,pitch,pos,meaning,example,mnemonic,insight}}
- hits:    [{word, sentence, mmss, time, ...}]  (from match_moji.py)
- deepdive (optional): a markdown file whose content is appended after the tables
  (the ljg-word style deep-dives, authored per video).
"""
import json, argparse

def esc(s): return str(s).replace("|", "｜")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matched", default="moji_matched.json")
    ap.add_argument("--hits", default="vocab_full_hits.json")
    ap.add_argument("--title", required=True)
    ap.add_argument("--url", default="")
    ap.add_argument("--deepdive", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    moji = json.load(open(a.matched, encoding="utf-8"))
    hits = json.load(open(a.hits, encoding="utf-8"))

    info = {}
    for h in hits:
        info.setdefault(h["word"], h)

    rows = []
    for aw, m in moji.items():
        h = info.get(aw)
        if not h:
            print("!! not found in video:", aw); continue
        rows.append({**m, "sentence": h["sentence"], "mmss": h["mmss"], "time": h["time"]})
    rows.sort(key=lambda r: r["time"])

    def table(level):
        out = ["| 序号 | 発音 | 音調 | 単語 | 词性 | 释义 | 例句 | 片中例句（时间） | 助记 | 深挖 |",
               "|---|---|---|---|---|---|---|---|---|---|"]
        i = 0
        for r in rows:
            if r["level"] != level: continue
            i += 1
            clip = f'{esc(r["sentence"])}（{r["mmss"]}）'
            out.append(f'| {i} | {r["reading"]} | {r["pitch"]} | {r["moji"]} | {esc(r["pos"])} '
                       f'| {esc(r["meaning"])} | {esc(r["example"])} | {clip} '
                       f'| {esc(r.get("mnemonic","—"))} | {esc(r.get("insight","—"))} |')
        return "\n".join(out)

    n2 = sum(1 for r in rows if r["level"] == "N2")
    n1 = sum(1 for r in rows if r["level"] == "N1")

    L = [f"# {a.title} · MOJi 考前对策 N1/N2 重点词命中表", ""]
    if a.url:
        L += [f"视频地址：[{a.url}]({a.url})", ""]
    L.append("规则：动画 ASR 转写 → fugashi 还原原形 → 与 **MOJi「考前对策」N1/N2 精选重点词表**"
             "求交集 → 命中词输出。发音/音调/词性/释义/例句 取自 MOJi 词表（权威）；"
             "片中例句+时间来自本集 ASR；助记/深挖为学习补充。")
    L.append(f"命中：N2 {n2} 词 / N1 {n1} 词，共 {len(rows)} 词。")
    L += ["", "## N2 精选重点词（命中本集）", table("N2"),
          "", "## N1 精选重点词（命中本集）", table("N1")]

    if a.deepdive:
        L += ["", "---", "", open(a.deepdive, encoding="utf-8").read()]

    open(a.out, "w", encoding="utf-8").write("\n".join(L))
    print(f"written {a.out}  rows={len(rows)} N2={n2} N1={n1}")

if __name__ == "__main__":
    main()
