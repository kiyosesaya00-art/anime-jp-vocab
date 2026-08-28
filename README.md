# anime-jp-vocab

从动画视频用**本地 ASR** 抽取 **N1/N2 难度**的日语**词汇**与**语法**，与 MOJi「考前对策」精选表求交集，
产出可直接背诵的**词汇表 + 语法表**（Markdown + 精美白底 HTML），并对重点词/句型做 `ljg-word` 式深挖。

> 一个 skill，两个产出。核心理念：**不堆砌简单词/基础句型**——只保留在本集台词中真实出现、
> 且命中 MOJi 精选重点表的项，天然滤掉 N4/N5。

## 效果示例

见 [`examples/gintama_ep393434/`](examples/gintama_ep393434/)（银魂 ep393434 01-02 合集）：

- `银魂ep393434_MOJi重点词表.md` / `.html` —— 命中 **41 词**（N2 14 / N1 27），
  含 发音·音调·词性·释义·例句·**片中例句(时间)**·助记·深挖，10 张完整深挖卡。
- `银魂ep393434_MOJi语法表.md` / `.html` —— 命中 **8 条**（N2 6 / N1 2），
  含 句型·接续·含义·MOJi例句·**片中例句(时间)**·辨析，4 张深挖卡。

HTML 为白底浅色主题，词表的**单词/释义/助记三列带背景色**便于记忆。

## 快速开始

```bash
bash scripts/setup.sh                              # 装 ffmpeg / BBDown / python 依赖
python3 scripts/asr.py <audio> asr_full.json [offset]   # 本地 ASR（词级时间戳）
python3 scripts/match_moji.py asr_full.json vocab_full_hits.json \
    --moji data/moji_n1.json data/moji_n2.json --min-conf 0.6   # 词汇匹配
python3 scripts/match_grammar.py                   # 语法匹配（内置全量句型库）
python3 scripts/build_table.py --matched data/moji_matched.json \
    --hits vocab_full_hits.json --title "<标题>" --url <url> \
    --deepdive deepdives.md --out out.md           # 出词表
python3 scripts/make_html.py out.md out.html       # 渲染 HTML
```

## 目录

```
SKILL.md                 # 技能说明（工作流 / 深挖标准）
scripts/
  setup.sh               # 依赖安装（幂等）
  asr.py                 # mlx-whisper 本地 ASR，词级时间戳
  match_moji.py          # fugashi 分词还原原形 + 匹配 MOJi 词表
  match_grammar.py       # 内置 N1 172 + N2 132 句型库，扫台词匹配语法
  build_table.py         # 组装词表 Markdown（可附 deepdive）
  make_html.py           # Markdown -> 白底 HTML（徽章/三列上色/深挖卡片）
data/
  moji_matched.json      # 已匹配词条（含全字段），亦作格式参考
  moji_n1.json / moji_n2.json   # ← 放入 MOJi 全量词表（见下）
  raw/                   # 放原始 MOJi 词表（markdown 表格）供解析
evals/evals.json         # 触发与质量校验
examples/gintama_ep393434/    # 银魂样例成品
```

## 词汇全量库（可选，越全命中越多）

`match_grammar.py` 已内置**全量语法库**。词汇的 MOJi 全量库需自备：把 MOJi「考前对策」
N1/N2 词表（markdown 表格：`序号|发音|音调|单词|词性|释义|例句`）放进 `data/raw/`，
按文件名前缀 `n1_*` / `n2_*` 标级别，然后写入 `data/moji_n1.json` / `moji_n2.json`
（键为「单词」，值含 reading/pitch/pos/meaning/example/level）。仓库已内置 `moji_matched.json`
作为格式参考与银魂样例数据。

## 依赖

- macOS (Apple Silicon 推荐)：`mlx-whisper` 本地跑 whisper-large-v3-turbo
- `fugashi` + `unidic-lite`：分词 / 原形 / 读音
- `ffmpeg`、`BBDown`（下 B 站音轨，可选）
- `markdown`（出 HTML）

## License

MIT
