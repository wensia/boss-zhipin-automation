#!/bin/bash

# Boss直聘自动化 - 一键启动所有服务

echo "🚀 启动 Boss直聘自动化 Electron 完整环境"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
ROOT_DIR="/Users/panyuhang/我的项目/编程/网站/Boss直聘自动化"

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在清理所有进程...${NC}"

    # 终止后台进程
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✓ 后端进程已终止${NC}"
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✓ 前端进程已终止${NC}"
    fi

    # 清理可能残留的进程
    pkill -f "uv run python -m app.main" 2>/dev/null
    pkill -f "vite.*13601" 2>/dev/null

    echo -e "${GREEN}✓ 清理完成${NC}"
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM EXIT

# 1. 启动后端
echo -e "${BLUE}[1/3] 启动后端服务...${NC}"
cd "$ROOT_DIR/backend"
uv run python -m app.main > /tmp/boss-backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${YELLOW}后端进程 PID: $BACKEND_PID${NC}"

# 等待后端启动
echo -e "${YELLOW}等待后端就绪...${NC}"
for i in {1..20}; do
    if curl -s http://localhost:27421/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后端服务已就绪${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 20 ]; then
        echo -e "${RED}✗ 后端启动超时${NC}"
        echo -e "${YELLOW}查看日志：tail -f /tmp/boss-backend.log${NC}"
        exit 1
    fi
done

# 2. 启动前端
echo ""
echo -e "${BLUE}[2/3] 启动前端服务...${NC}"
cd "$ROOT_DIR/frontend"
npm run dev > /tmp/boss-frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${YELLOW}前端进程 PID: $FRONTEND_PID${NC}"

# 等待前端启动
echo -e "${YELLOW}等待前端就绪...${NC}"
for i in {1..20}; do
    if curl -s http://localhost:13601 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 前端服务已就绪${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 20 ]; then
        echo -e "${RED}✗ 前端启动超时${NC}"
        echo -e "${YELLOW}查看日志：tail -f /tmp/boss-frontend.log${NC}"
        exit 1
    fi
done

# 3. 启动 Electron
echo ""
echo -e "${BLUE}[3/3] 启动 Electron 应用...${NC}"
cd "$ROOT_DIR/electron-app"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}首次运行，安装依赖...${NC}"
    npm install
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ 所有服务已启动！${NC}"
echo ""
echo -e "  后端: ${BLUE}http://localhost:27421${NC}"
echo -e "  前端: ${BLUE}http://localhost:13601${NC}"
echo ""
echo -e "${YELLOW}提示：${NC}"
echo -e "  - Electron 窗口即将打开"
echo -e "  - 关闭窗口后，按 Ctrl+C 停止所有服务"
echo -e "  - 后端日志：tail -f /tmp/boss-backend.log"
echo -e "  - 前端日志：tail -f /tmp/boss-frontend.log"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 启动 Electron（前台运行）
npm start

# Electron 退出后自动清理
cleanup
