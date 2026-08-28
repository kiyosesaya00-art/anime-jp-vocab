import sys, json
import mlx_whisper

audio = sys.argv[1]
out = sys.argv[2]
offset = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

print("loading + transcribing:", audio, flush=True)
r = mlx_whisper.transcribe(
    audio,
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
    language="ja",
    word_timestamps=True,
    verbose=False,
)
segs = []
for s in r["segments"]:
    words = [
        {"w": w["word"], "s": round(w["start"] + offset, 2),
         "p": round(float(w.get("probability", 0)), 3)}
        for w in s.get("words", [])
    ]
    segs.append({
        "start": round(s["start"] + offset, 2),
        "text": s["text"],
        "words": words,
    })
json.dump(segs, open(out, "w"), ensure_ascii=False, indent=1)
print("SEGMENTS", len(segs), "-> ", out, flush=True)
