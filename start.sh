#!/bin/bash

# ============================================
# Boss直聘自动化工具 - macOS 启动脚本
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
PID_FILE="$SCRIPT_DIR/.backend.pid"
PORT=27421

# 打印函数
print_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 清理函数
cleanup() {
    echo ""
    print_info "正在停止服务..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null
            print_success "服务已停止"
        fi
        rm -f "$PID_FILE"
    fi
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

# 检查端口是否被占用
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 开始
echo ""
echo "============================================"
echo "   Boss直聘自动化工具 - 启动中..."
echo "============================================"
echo ""

# 检查端口
if check_port; then
    print_warning "端口 $PORT 已被占用"
    
    # 检查是否是我们的进程
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            print_info "检测到已有服务在运行 (PID: $OLD_PID)"
            print_info "正在打开浏览器..."
            open "http://localhost:$PORT"
            print_success "浏览器已打开，访问: http://localhost:$PORT"
            echo ""
            print_info "如需停止服务，请运行: ./stop.sh"
            exit 0
        fi
    fi
    
    print_error "请先停止占用端口 $PORT 的程序"
    print_info "运行以下命令查看占用进程:"
    echo "    lsof -i :$PORT"
    print_info "或运行 ./stop.sh 停止服务"
    exit 1
fi

# 确保 uv 可用
export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv &> /dev/null; then
    print_error "未找到 uv，请先运行 ./install.sh"
    exit 1
fi

cd "$BACKEND_DIR"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    print_info "首次运行，正在安装依赖..."
    uv sync
fi

# 检查 Playwright 浏览器
print_info "检查 Playwright 浏览器..."
CHROMIUM_PATH=$(uv run python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null || echo "")

if [ -z "$CHROMIUM_PATH" ] || [ ! -f "$CHROMIUM_PATH" ]; then
    print_warning "Playwright 浏览器未安装，正在安装..."
    uv run playwright install chromium
    
    # 再次检查
    CHROMIUM_PATH=$(uv run python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null || echo "")
    
    if [ -z "$CHROMIUM_PATH" ] || [ ! -f "$CHROMIUM_PATH" ]; then
        print_error "Playwright 浏览器安装失败"
        print_info "请手动运行: uv run playwright install chromium"
        exit 1
    fi
fi
print_success "Playwright 浏览器已就绪"

# 检查前端构建
if [ ! -f "$SCRIPT_DIR/frontend/dist/index.html" ]; then
    print_warning "前端未构建，请先运行 ./install.sh"
fi

echo ""
echo "============================================"
print_success "访问地址: http://localhost:$PORT"
echo "============================================"
echo ""
print_info "按 Ctrl+C 停止服务"
echo ""

# 启动后端服务
uv run python -m app.main &
BACKEND_PID=$!

# 保存 PID
echo $BACKEND_PID > "$PID_FILE"

# 等待服务启动
sleep 2

# 检查服务是否成功启动
if kill -0 $BACKEND_PID 2>/dev/null; then
    print_success "服务启动成功"
    print_info "正在打开浏览器..."
    
    # 打开浏览器
    if command -v open &> /dev/null; then
        open "http://localhost:$PORT"
    fi
else
    print_error "服务启动失败"
    rm -f "$PID_FILE"
    exit 1
fi

# 等待后端进程
wait $BACKEND_PID
