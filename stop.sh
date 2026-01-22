#!/bin/bash

# ============================================
# Boss直聘自动化工具 - macOS 停止脚本
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
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

echo ""
echo "============================================"
echo "   Boss直聘自动化工具 - 停止服务"
echo "============================================"
echo ""

STOPPED=false

# 方法1: 通过 PID 文件停止
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        print_info "正在停止服务 (PID: $PID)..."
        kill "$PID" 2>/dev/null
        sleep 1
        
        # 检查是否还在运行
        if kill -0 "$PID" 2>/dev/null; then
            print_warning "进程未响应，强制终止..."
            kill -9 "$PID" 2>/dev/null
        fi
        
        STOPPED=true
    fi
    rm -f "$PID_FILE"
fi

# 方法2: 通过端口查找并停止
PIDS=$(lsof -ti :$PORT 2>/dev/null)
if [ -n "$PIDS" ]; then
    for PID in $PIDS; do
        if kill -0 "$PID" 2>/dev/null; then
            print_info "正在停止端口 $PORT 上的进程 (PID: $PID)..."
            kill "$PID" 2>/dev/null
            sleep 1
            
            # 强制终止
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID" 2>/dev/null
            fi
            
            STOPPED=true
        fi
    done
fi

# 清理 Playwright 浏览器进程
CHROMIUM_PIDS=$(pgrep -f "chromium.*--remote-debugging" 2>/dev/null || true)
if [ -n "$CHROMIUM_PIDS" ]; then
    print_info "正在关闭 Playwright 浏览器..."
    for PID in $CHROMIUM_PIDS; do
        kill "$PID" 2>/dev/null || true
    done
fi

if [ "$STOPPED" = true ]; then
    print_success "服务已停止"
else
    print_info "没有发现正在运行的服务"
fi

echo ""
