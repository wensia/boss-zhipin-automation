#!/bin/bash

# Boss直聘自动化工具 - 首次安装脚本
# 只需运行一次，之后使用 start.sh 启动

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "====================================="
echo "   Boss直聘自动化工具 - 首次安装"
echo "====================================="

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 请先安装 Node.js (仅首次安装需要)"
    echo "下载地址: https://nodejs.org/"
    exit 1
fi

# 安装 uv
if ! command -v uv &> /dev/null; then
    echo ""
    echo "[1/4] 安装 uv (Python 包管理器)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "[1/4] uv 已安装"
fi

# 安装后端依赖
echo ""
echo "[2/4] 安装后端依赖..."
cd "$BACKEND_DIR"
uv sync

# 安装 Playwright 浏览器
echo ""
echo "[3/4] 安装 Playwright 浏览器..."
uv run playwright install chromium

# 构建前端
echo ""
echo "[4/4] 构建前端..."
cd "$FRONTEND_DIR"
npm install
npm run build

echo ""
echo "====================================="
echo "   安装完成!"
echo "====================================="
echo ""
echo "现在可以运行 ./start.sh 启动应用"
echo ""
