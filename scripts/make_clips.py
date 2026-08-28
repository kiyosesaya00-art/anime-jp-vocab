#!/usr/bin/env python3
"""Slice per-example audio clips from the source track, for click-to-play.

For every hit time (segment start) referenced by the vocab/grammar tables,
cut a small clip [start, end] with ffmpeg into <out-dir>/cXXXX.m4a
(XXXX = round(start*100), so build_table.py can derive the same filename).

Usage:
  python3 make_clips.py \
      --asr asr_full.json \
      --audio "audio/xxx.m4a" \
      --hits vocab_full_hits.json grammar_hits_raw.json \
      --out-dir clips [--offset 0] [--pad 0.15] [--max 8]

end of each clip = next segment start (capped by --max seconds);
--offset is subtracted from hit times if the audio is a sub-segment of the
episode (hit times store start+offset; default 0 = single full track).
"""
import sys, json, argparse, subprocess, os, shutil

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--hits", nargs="+", required=True)
    ap.add_argument("--out-dir", default="clips")
    ap.add_argument("--offset", type=float, default=0.0)
    ap.add_argument("--pad", type=float, default=0.15)
    ap.add_argument("--max", type=float, default=8.0)
    a = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH (run scripts/setup.sh).")

    segs = json.load(open(a.asr, encoding="utf-8"))
    starts = sorted({round(s["start"], 2) for s in segs})

    def seg_end(t):
        # end = next distinct segment start after t, capped by --max
        for s in starts:
            if s > t + 0.05:
                return min(s, t + a.max)
        return t + min(4.0, a.max)

    times = set()
    for hp in a.hits:
        for h in json.load(open(hp, encoding="utf-8")):
            if "time" in h:
                times.add(round(float(h["time"]), 2))

    os.makedirs(a.out_dir, exist_ok=True)
    made = 0
    for t in sorted(times):
        cid = int(round(t * 100))
        out = os.path.join(a.out_dir, f"c{cid}.m4a")
        if os.path.exists(out) and os.path.getsize(out) > 0:
            made += 1
            continue
        ss = max(0.0, t - a.offset - a.pad)
        dur = (seg_end(t) - t) + a.pad + 0.2
        r = subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{ss:.2f}", "-i", a.audio,
             "-t", f"{dur:.2f}", "-vn", "-map", "0:a:0",
             "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
             "-loglevel", "error", out],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print("!! ffmpeg failed at", t, r.stderr[:200]); continue
        made += 1
    print(f"clips ready: {made}/{len(times)} -> {a.out_dir}/")

if __name__ == "__main__":
    main()
