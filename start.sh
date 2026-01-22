#!/bin/bash

# Boss直聘自动化工具 - 一键启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "====================================="
echo "   Boss直聘自动化工具 - 启动中..."
echo "====================================="

# 安装 uv (如果没有)
if ! command -v uv &> /dev/null; then
    echo ""
    echo "正在安装 uv (Python 包管理器)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

cd "$BACKEND_DIR"

# 首次运行时安装依赖
if [ ! -d ".venv" ]; then
    echo ""
    echo "首次运行，正在安装依赖..."
    uv sync
    echo ""
    echo "正在安装 Playwright 浏览器..."
    uv run playwright install chromium
fi

echo ""
echo "====================================="
echo "   访问地址: http://localhost:27421"
echo "====================================="
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 后台启动后端，等待启动完成后打开浏览器
uv run python -m app.main &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 检查后端是否成功启动
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "正在打开浏览器..."
    open "http://localhost:27421"
fi

# 等待后端进程
wait $BACKEND_PID
