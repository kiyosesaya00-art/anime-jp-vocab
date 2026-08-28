import sys, re, markdown

SRC = sys.argv[1] if len(sys.argv) > 1 else "银魂ep393434_词汇表_full.md"
OUT = sys.argv[2] if len(sys.argv) > 2 else SRC.rsplit(".", 1)[0] + ".html"

md_text = open(SRC, encoding="utf-8").read()
# 提取标题（首个 # 行）
m = re.search(r"^#\s+(.+)$", md_text, re.M)
title = m.group(1).strip() if m else "日语学习词表"

body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
)

# 级别徽章：给表格里的 N1/N2/表外 单元格上色（简单后处理）
def badge(mobj):
    lv = mobj.group(1)
    cls = {"N1": "lv-n1", "N2": "lv-n2", "表外": "lv-ex"}.get(lv, "")
    return f'<td><span class="badge {cls}">{lv}</span></td>'
body = re.sub(r"<td>(N1|N2|表外)</td>", badge, body)

CSS = """
<style>
:root{--bg:#f7f8fa;--card:#ffffff;--fg:#1f2430;--mut:#6b7280;--line:#e5e7eb;
--n1:#dc2626;--n2:#d97706;--ex:#7c3aed;--accent:#2563eb;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,"PingFang SC","Hiragino Sans","Noto Sans CJK SC",Segoe UI,sans-serif;
line-height:1.7;font-size:15px}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
h1{font-size:26px;margin:0 0 6px;letter-spacing:.5px}
h1+p,h1+p+p{color:var(--mut);font-size:13.5px;margin:4px 0}
a{color:var(--accent);text-decoration:none;border-bottom:1px dashed rgba(37,99,235,.5)}
a:hover{border-bottom-style:solid}
h2{font-size:20px;margin:38px 0 4px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:17px;margin:26px 0 10px;color:#111827;
background:linear-gradient(90deg,rgba(37,99,235,.10),transparent);
padding:8px 12px;border-left:3px solid var(--accent);border-radius:4px}
hr{border:0;border-top:1px solid var(--line);margin:34px 0}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px;
background:var(--card);border-radius:10px;overflow:hidden;
box-shadow:0 1px 3px rgba(0,0,0,.06)}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f1f3f7;color:#374151;font-weight:600;position:sticky;top:0}
tr:hover td{background:#f5f7fb}
td:nth-child(3){color:var(--mut);white-space:nowrap}
/* MOJi 表三列上色，好看好记：单词 / 释义 / 助记 */
td.col-word{background:#e8f0ff;color:#173a8a;font-weight:800;border-left:3px solid #8fb2f2;white-space:nowrap}
td.col-mean{background:#e7f8ee;color:#14532d;font-weight:600}
td.col-mnemo{background:#fff3e0;color:#8a4b00}
tr:hover td.col-word{background:#dbe7ff}
tr:hover td.col-mean{background:#dbf3e2}
tr:hover td.col-mnemo{background:#ffe9c9}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:700}
.lv-n1{background:rgba(220,38,38,.10);color:var(--n1);border:1px solid rgba(220,38,38,.35)}
.lv-n2{background:rgba(217,119,6,.10);color:var(--n2);border:1px solid rgba(217,119,6,.35)}
.lv-ex{background:rgba(124,58,237,.10);color:var(--ex);border:1px solid rgba(124,58,237,.35)}
ul{margin:8px 0;padding-left:22px}
li{margin:4px 0}
strong{color:#111827}
blockquote{margin:10px 0;padding:10px 14px;background:#fff8ec;border-left:3px solid var(--n2);
border-radius:4px;color:#7c4a03;font-style:normal}
code{background:#eef1f6;padding:2px 6px;border-radius:5px;font-size:13px;color:#1d4ed8}
.deepdive{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:4px 18px 14px;margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.play{display:inline-block;margin-left:6px;padding:1px 8px;border-radius:999px;
background:#eef4ff;color:#1d4ed8;border:1px solid #b9cdfa;font-size:12px;
font-weight:700;cursor:pointer;white-space:nowrap;user-select:none}
.play:hover{background:#dbe7ff}
.play.playing{background:#1d4ed8;color:#fff;border-color:#1d4ed8}
</style>
"""

# 把每个 ### 深挖块包进卡片
def wrap_cards(html):
    parts = re.split(r"(<h3>.*?</h3>)", html)
    out, i = [], 0
    while i < len(parts):
        seg = parts[i]
        if seg.startswith("<h3>"):
            # 收集到下一个 h3 / h2 / hr 之前
            j = i + 1
            buf = seg
            while j < len(parts) and not parts[j].startswith("<h3>"):
                buf += parts[j]; j += 1
            out.append(f'<div class="deepdive">{buf}</div>')
            i = j
        else:
            out.append(seg); i += 1
    return "".join(out)

body = wrap_cards(body)

# 只给 10 列的 MOJi 表上色：第4列单词 / 第6列释义 / 第9列助记
def color_cols(html):
    COLS = {3: "col-word", 5: "col-mean", 8: "col-mnemo"}
    def repl(m):
        inner = m.group(1)
        parts = re.split(r"(<td>.*?</td>)", inner, flags=re.S)
        n, rebuilt = 0, []
        for p in parts:
            if re.fullmatch(r"<td>.*?</td>", p, re.S):
                c = COLS.get(n)
                if c:
                    p = p.replace("<td>", f'<td class="{c}">', 1)
                n += 1
            rebuilt.append(p)
        if n != 10:
            return m.group(0)
        return "<tr>" + "".join(rebuilt) + "</tr>"
    return re.sub(r"<tr>(.*?)</tr>", repl, html, flags=re.S)

body = color_cols(body)

html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{CSS}
</head><body><div class="wrap">
{body}
<p style="color:#5b6472;margin-top:40px;font-size:12px;text-align:center">
Generated by anime-jp-vocab · ASR + fugashi + JLPT + wordfreq</p>
</div>
<script>
document.addEventListener('click', function(e){{
  var el = e.target.closest('.play'); if(!el) return;
  var src = el.getAttribute('data-src'); if(!src) return;
  if(window.__cur){{ window.__cur.a.pause(); window.__cur.el.classList.remove('playing'); }}
  var a = new Audio(src);
  window.__cur = {{a:a, el:el}};
  el.classList.add('playing');
  a.play().catch(function(){{ el.classList.remove('playing'); }});
  a.onended = function(){{ el.classList.remove('playing'); }};
}});
</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(html)
print("written", OUT, f"({len(html)} bytes)")
