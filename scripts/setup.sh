#!/usr/bin/env bash
# 幂等安装依赖：ffmpeg / BBDown / Python 包。已装则跳过。
set -e
export PATH="$HOME/.local/bin:$PATH"
mkdir -p "$HOME/.local/bin"

echo "==> Python 包 (mlx-whisper / fugashi / unidic-lite / markdown)"
python3 -m pip install -q --upgrade \
  mlx-whisper fugashi unidic-lite markdown \
  -i https://mirrors.aliyun.com/pypi/simple/ || {
    echo "pip 安装失败，请检查网络或换源"; exit 1; }

echo "==> ffmpeg"
if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then brew install ffmpeg;
  else echo "!! 未找到 ffmpeg，且无 brew。请手动安装 ffmpeg。"; fi
else echo "ffmpeg 已安装"; fi

echo "==> BBDown (可选，用于下载 B 站视频音轨)"
if ! command -v BBDown >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/BBDown" ]; then
  echo "   如需从 B 站取音轨，请安装 BBDown 到 ~/.local/bin"
  echo "   https://github.com/nilaoda/BBDown/releases"
else echo "BBDown 已就绪"; fi

echo "==> 完成。Apple Silicon 上 mlx-whisper 首次运行会自动下载模型。"
