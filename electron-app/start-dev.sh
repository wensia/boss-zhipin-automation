#!/bin/bash

# Boss直聘自动化 - Electron 开发模式启动脚本

echo "🚀 启动 Boss直聘自动化 Electron 开发模式"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查后端服务
echo -e "${YELLOW}检查后端服务...${NC}"
if curl -s http://localhost:27421/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务已运行${NC}"
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo -e "${YELLOW}请先启动后端服务：${NC}"
    echo "  cd ../backend && uv run python -m app.main"
    exit 1
fi

# 检查前端服务
echo -e "${YELLOW}检查前端服务...${NC}"
if curl -s http://localhost:13601 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端服务已运行${NC}"
else
    echo -e "${RED}✗ 前端服务未运行${NC}"
    echo -e "${YELLOW}请先启动前端服务：${NC}"
    echo "  cd ../frontend && npm run dev"
    exit 1
fi

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}首次运行，安装依赖...${NC}"
    npm install
fi

# 启动 Electron
echo ""
echo -e "${GREEN}✓ 所有服务就绪，启动 Electron...${NC}"
echo ""
npm start
