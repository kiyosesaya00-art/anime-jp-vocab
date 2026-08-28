---
name: anime-jp-vocab
description: 从动画视频（B站番剧等）用本地 ASR 抽取 N1/N2 难度日语词汇，与 MOJi「考前对策」精选重点词表求交集，产出带发音/音调/词性/释义/例句/片中例句时间/助记/深挖的词汇表（Markdown + 精美 HTML）。触发场景：用户想「从某动画/番剧里学日语单词」「提取这集的 N1/N2 词汇」「给动画做日语词表/生词本」「银魂/某番 的重点词」等。
version: "1.0.0"
user_invocable: true
---

# anime-jp-vocab · 动画日语重点词抽取

把一集动画变成一张「**只含 N1/N2 难词**、可直接背诵」的词汇表：
发音 · 音调 · 词性 · 释义 · 例句 · **片中例句+时间** · 助记 · **深挖**。

核心理念：**不堆砌简单词**。只保留同时满足两个条件的词——
1. 在本集台词中真实出现（ASR 转写 + fugashi 还原原形）；
2. 命中 **MOJi「考前对策」N1/N2 精选重点词表**（权威难度背书，天然滤掉 N4/N5 简单词）。

## 依赖

```bash
bash scripts/setup.sh
```
装：`ffmpeg`、`BBDown`（下 B 站视频/音轨）、Python 包 `mlx-whisper`（Apple Silicon 本地 ASR）、
`fugashi`+`unidic-lite`（分词/还原原形/读音）、`markdown`（出 HTML）。

## 词表数据（一次性准备）

把 MOJi「考前对策」N1/N2 词表（markdown 表格）放进 `data/raw/`，字段顺序：
`序号 | 发音 | 音调 | 单词 | 词性 | 释义 | 例句`。文件名建议 `n1_*.md` / `n2_*.md`，
用文件名前缀标记级别。然后：

```bash
python3 scripts/parse_moji.py     # data/raw/*.md -> data/moji_n1.json / data/moji_n2.json
```

仓库已内置 `data/moji_matched.json`（银魂样例命中的 41 词，含完整字段），
可直接作为格式参考；`data/moji_n1.json`/`moji_n2.json` 为全量参考库（越全，可命中越多）。

## 整体流程（5 步）

> **执行前必做 · 询问是否需要片中例句原声**
> 由于整集 ASR 已较耗时，「片中例句可点击播放原声」（Step 5 切片）为**可选项**。
> 开工前先用弹窗询问用户，并说明代价：
> - **需要原声**：多做 Step 5，按命中例句用 ffmpeg 逐条切片，**额外约 1–2 分钟**
>   （随命中/例句条数增加；生成的 HTML 需连同 `clips/` 目录一起分享才能离线点播）。
> - **不需要原声**：跳过 Step 5，片中例句只显示时间戳（不可点击），**出表更快**。
>
> 拿到用户选择后再执行；未选择前不要贸然开始切片。


### Step 1　取音轨
用 BBDown 下目标视频音频（或用户已有的音视频文件）。合集/多 P 需注意片段偏移 `offset`（秒），
用于把分段时间轴对齐到整集。

### Step 2　本地 ASR（词级时间戳）
```bash
python3 scripts/asr.py <audio> asr_full.json [offset]
```
输出每段 `{start, text, words:[{w,s,p}]}`，`p` 为词级置信度，供后续过滤。

### Step 3　分词 + 匹配 MOJi 重点词
```bash
python3 scripts/match_moji.py asr_full.json vocab_full_hits.json \
    --moji data/moji_n1.json data/moji_n2.json --min-conf 0.6
```
- fugashi 还原**原形(lemma)** 与**读音**；
- 与 MOJi 头词表求交集（同时按读音兜底匹配假名词如「まとも」）；
- 词级置信度 `p >= min-conf` 过滤 ASR 噪声；
- 记录每词**首次出现的整句 + mm:ss**。

### Step 4　出表 + 渲染 HTML
```bash
python3 scripts/build_table.py     # -> <标题>_MOJi重点词表.md
python3 scripts/make_html.py <标题>_MOJi重点词表.md <标题>_MOJi重点词表.html
```
表格列：`序号 | 发音 | 音调 | 单词 | 词性 | 释义 | 例句 | 片中例句（时间） | 助记 | 深挖`，
按 N2 / N1 分组。HTML 为**白底浅色主题**，**单词/释义/助记三列带背景色**便于记忆。

### Step 5　切片原声（片中例句点击即播）
`build_table.py` 会把「片中例句」的时间戳渲染成可点击的 `🔊mm:ss` 按钮，指向
`clips/c<起始厘秒>.m4a`。用 ffmpeg 从音轨切出对应小片段：

```bash
python3 scripts/make_clips.py \
    --asr asr_full.json \
    --audio <audio> \
    --hits vocab_full_hits.json \
    --out-dir clips [--offset 0]
```
- 每个片中例句时间切一段 `[start, 下一句 start]`（上限 `--max` 秒），命名 `c<round(start*100)>.m4a`，
  与表格里的 `data-src` 自动对齐；重复时间共用同一片段；
- 合集/多 P 若音轨是子片段，用 `--offset` 把整集时间轴换算回本段音轨；
- HTML 用相对路径引用 `clips/`，**把 `.html` 和 `clips/` 目录一起拷贝/分享即可离线点播**；
- 语法表由同一 `build_table.py` 渲染，故同样自带点播按钮，对其 `--hits` 跑一次 `make_clips.py` 即可。

## 语法抽取（第二产出）

同一份 `asr_full.json`，再跑语法匹配（无需重新下载/ASR）：

```bash
python3 scripts/match_grammar.py     # 读 asr_full.json -> grammar_hits_raw.json
```
- `match_grammar.py` **内置全量 MOJi 语法句型库**（N1 172 条 + N2 132 条，重复归 N2）；
- 把句型规范化为检索 token，扫全集台词求交集；短词/常见词进 `STOP` 表防误报；
- 输出原始命中后，**务必人工核验剔除 substring 假命中**（如「ひょんな**ことか**ら」误触 ことか、「気に**して**」误触 にして、「そこ**までだ**」误触 までだ）；
- 被短词过滤漏掉但真实出现的（如 すら）手动补回。

语法表列：`# | 句型 | 接续 | 级别 | 含义 | 例句（MOJi） | 片中例句（时间） | 辨析·助记`，
含义/例句取自 MOJi 语法表，片中例句+时间来自 ASR。重点句型加深挖（接续·语感·近义辨析，
如 どころか vs ばかりか、すら vs さえ、くせに vs のに）。

> **一个 skill，两个产出**：词汇表 + 语法表，共享 Step 1–2 的下载与 ASR。

## 深挖（必做·标准）

对每张词表，挑选 **中日汉字含义差异大 / 难词**，仿 `ljg-word` 写**完整深挖**：

1. **原始画面**：该词最物理的源头画面；
2. **核心意象**：提炼公式（如 涩=收敛不甜腻 → 老练有味）；
3. **解释**：2–4 段有穿透力的阐述，**加粗关键词**，打通词源·汉字构造·多领域用法·**中日对比**；
4. **一语道破**：一句中日双语金句；
5. **速记**：难词再给谐音/惯用句锚点。

> 「解释」段是深挖的灵魂，不可省略成骨架。宁可少挖几个词，也要每个挖透。

## 输出给用户

给出成品文件路径（.md + .html + `clips/` 目录）、命中词数（N2/N1 各多少）、几条亮点深挖示例，
并提示「片中例句的 🔊 时间戳可点击播放原声，分享时连同 `clips/` 一起拷贝」。
样例见 `examples/gintama_ep393434/`（银魂 ep393434 01-02 合集，命中 41 词 + 10 张深挖卡，片中例句可点播）。
