#!/bin/bash

# ============================================
# Boss直聘自动化工具 - macOS 安装脚本
# 首次使用时运行一次即可
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# 打印带颜色的消息
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

# 错误处理
handle_error() {
    print_error "安装过程中出现错误，请检查上面的错误信息"
    print_info "如果问题持续，请尝试："
    print_info "  1. 检查网络连接"
    print_info "  2. 重新运行此脚本"
    print_info "  3. 联系开发者获取帮助"
    exit 1
}

trap handle_error ERR

# 开始安装
echo ""
echo "============================================"
echo "   Boss直聘自动化工具 - 首次安装"
echo "============================================"
echo ""

# 检查操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "此脚本为 macOS 设计，其他系统可能无法正常运行"
fi

# ============================================
# 步骤 1: 安装 uv (Python 包管理器)
# ============================================
echo ""
print_info "[1/4] 检查 uv (Python 包管理器)..."

if command -v uv &> /dev/null; then
    print_success "uv 已安装: $(uv --version)"
else
    print_info "正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # 添加到当前 shell 环境
    export PATH="$HOME/.local/bin:$PATH"

    if command -v uv &> /dev/null; then
        print_success "uv 安装成功: $(uv --version)"
    else
        print_error "uv 安装失败，请手动安装: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# ============================================
# 步骤 2: 安装后端依赖
# ============================================
echo ""
print_info "[2/4] 安装后端依赖..."

cd "$BACKEND_DIR"

if [ -d ".venv" ]; then
    print_info "发现已有虚拟环境，正在更新依赖..."
fi

uv sync

if [ -d ".venv" ]; then
    print_success "后端依赖安装成功"
else
    print_error "后端依赖安装失败"
    exit 1
fi

# ============================================
# 步骤 3: 安装 Playwright 浏览器
# ============================================
echo ""
print_info "[3/4] 安装 Playwright 浏览器 (Chromium)..."
print_info "这可能需要几分钟，请耐心等待..."

cd "$BACKEND_DIR"

# 获取 Playwright 期望的浏览器路径
EXPECTED_PATH=$(uv run python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null || echo "")

# 检查浏览器是否已存在
if [ -n "$EXPECTED_PATH" ] && [ -f "$EXPECTED_PATH" ]; then
    print_success "Playwright Chromium 已安装"
else
    print_info "正在下载 Chromium 浏览器..."
    
    # 安装到系统缓存目录（默认位置）
    uv run playwright install chromium
    
    # 再次验证
    CHROMIUM_PATH=$(uv run python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null || echo "")
    
    if [ -n "$CHROMIUM_PATH" ] && [ -f "$CHROMIUM_PATH" ]; then
        print_success "Playwright Chromium 安装成功"
    else
        # 尝试强制安装
        print_warning "首次安装未成功，尝试强制安装..."
        uv run playwright install chromium --force
        
        # 最终验证
        FINAL_PATH=$(uv run python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null || echo "")
        
        if [ -n "$FINAL_PATH" ] && [ -f "$FINAL_PATH" ]; then
            print_success "Playwright Chromium 安装成功"
        else
            print_warning "Playwright 浏览器安装可能不完整"
            print_info "请手动运行: cd backend && uv run playwright install chromium"
        fi
    fi
fi

# ============================================
# 步骤 4: 检查前端构建
# ============================================
echo ""
print_info "[4/4] 检查前端构建..."

cd "$FRONTEND_DIR"

if [ -d "dist" ] && [ -f "dist/index.html" ]; then
    print_success "前端已构建完成"
else
    print_info "前端未构建，检查 Node.js..."

    if command -v node &> /dev/null; then
        print_info "Node.js 版本: $(node --version)"
        print_info "正在构建前端..."

        npm install --legacy-peer-deps 2>/dev/null || npm install
        npm run build

        if [ -f "dist/index.html" ]; then
            print_success "前端构建成功"
        else
            print_error "前端构建失败"
            exit 1
        fi
    else
        print_warning "未检测到 Node.js，跳过前端构建"
        print_info "如需重新构建前端，请先安装 Node.js: https://nodejs.org/"
        print_info "然后运行: cd frontend && npm install && npm run build"
    fi
fi

# ============================================
# 安装完成
# ============================================
echo ""
echo "============================================"
print_success "安装完成!"
echo "============================================"
echo ""
print_info "现在可以运行以下命令启动应用:"
echo ""
echo "    ./start.sh"
echo ""
print_info "访问地址: http://localhost:27421"
echo ""
