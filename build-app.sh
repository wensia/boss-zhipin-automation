#!/bin/bash

# Boss直聘自动化工具 - 一键打包脚本
# 用于生成 Mac DMG 安装包

set -e

echo "=================================="
echo "  Boss直聘自动化工具 - 打包脚本"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 步骤 1: 检查依赖
echo -e "${YELLOW}[1/5] 检查依赖...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未安装 Node.js${NC}"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo -e "${RED}错误: 未安装 uv${NC}"
    echo "请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}✓ 依赖检查通过${NC}"

# 步骤 2: 安装 Playwright 浏览器（如果需要）
echo ""
echo -e "${YELLOW}[2/5] 检查 Playwright 浏览器...${NC}"

PLAYWRIGHT_CACHE="$HOME/Library/Caches/ms-playwright"
if [ ! -d "$PLAYWRIGHT_CACHE" ] || [ -z "$(ls -A $PLAYWRIGHT_CACHE 2>/dev/null | grep chromium)" ]; then
    echo "正在安装 Playwright Chromium..."
    cd backend
    uv run playwright install chromium
    cd ..
    echo -e "${GREEN}✓ Playwright Chromium 安装完成${NC}"
else
    echo -e "${GREEN}✓ Playwright Chromium 已安装${NC}"
fi

# 步骤 3: 安装后端依赖
echo ""
echo -e "${YELLOW}[3/5] 安装后端依赖...${NC}"
cd backend
uv sync
# 确保 pyinstaller 已安装
uv add pyinstaller --dev 2>/dev/null || true
cd ..
echo -e "${GREEN}✓ 后端依赖安装完成${NC}"

# 步骤 4: 安装前端和 Electron 依赖
echo ""
echo -e "${YELLOW}[4/5] 安装前端依赖...${NC}"
cd frontend
npm install
cd ..

cd electron-app
npm install
cd ..
echo -e "${GREEN}✓ 前端依赖安装完成${NC}"

# 步骤 5: 构建应用
echo ""
echo -e "${YELLOW}[5/5] 构建 Mac 应用...${NC}"
echo "这可能需要几分钟，请耐心等待..."
echo ""

cd electron-app
npm run build

echo ""
echo "=================================="
echo -e "${GREEN}  ✓ 打包完成！${NC}"
echo "=================================="
echo ""
echo "DMG 文件位置:"
echo "  $SCRIPT_DIR/electron-app/dist/"
echo ""
ls -la dist/*.dmg 2>/dev/null || echo "（查找 DMG 文件...）"
echo ""
echo "将 DMG 文件发送给用户即可使用。"
