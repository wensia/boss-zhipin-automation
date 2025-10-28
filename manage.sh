#!/bin/bash

# Boss直聘自动化 - 启停控制脚本
# 用法: ./manage.sh [start|stop|restart|status] [frontend|backend|all]

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 加载端口配置
if [ -f .ports ]; then
    source .ports
else
    echo "错误: 端口配置文件 .ports 不存在"
    exit 1
fi

# PID文件路径
FRONTEND_PID="$SCRIPT_DIR/.frontend.pid"
BACKEND_PID="$SCRIPT_DIR/.backend.pid"

# 日志文件
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_LOG="$LOG_DIR/backend.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查进程是否运行
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# 启动前端
start_frontend() {
    if is_running "$FRONTEND_PID"; then
        log_warn "前端已经在运行中 (PID: $(cat $FRONTEND_PID))"
        return 1
    fi

    log_info "启动前端服务 (端口: $FRONTEND_PORT)..."
    cd "$SCRIPT_DIR/frontend"

    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        log_info "检测到未安装依赖，正在安装..."
        npm install
    fi

    # 启动前端开发服务器
    nohup npm run dev -- --port "$FRONTEND_PORT" --host 0.0.0.0 > "$FRONTEND_LOG" 2>&1 &
    echo $! > "$FRONTEND_PID"

    sleep 2
    if is_running "$FRONTEND_PID"; then
        log_success "前端服务启动成功"
        log_info "访问地址: http://localhost:$FRONTEND_PORT"
        log_info "日志文件: $FRONTEND_LOG"
    else
        log_error "前端服务启动失败，请查看日志: $FRONTEND_LOG"
        return 1
    fi
}

# 启动后端
start_backend() {
    if is_running "$BACKEND_PID"; then
        log_warn "后端已经在运行中 (PID: $(cat $BACKEND_PID))"
        return 1
    fi

    log_info "启动后端服务 (端口: $BACKEND_PORT)..."
    cd "$SCRIPT_DIR/backend"

    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        log_error "虚拟环境不存在，请先运行 'cd backend && uv sync'"
        return 1
    fi

    # 加载环境变量
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi

    # 启动后端服务器
    nohup uv run uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload > "$BACKEND_LOG" 2>&1 &
    echo $! > "$BACKEND_PID"

    sleep 2
    if is_running "$BACKEND_PID"; then
        log_success "后端服务启动成功"
        log_info "API地址: http://localhost:$BACKEND_PORT"
        log_info "API文档: http://localhost:$BACKEND_PORT/docs"
        log_info "日志文件: $BACKEND_LOG"
    else
        log_error "后端服务启动失败，请查看日志: $BACKEND_LOG"
        return 1
    fi
}

# 停止前端
stop_frontend() {
    if ! is_running "$FRONTEND_PID"; then
        log_warn "前端服务未运行"
        return 1
    fi

    log_info "停止前端服务..."
    local pid=$(cat "$FRONTEND_PID")

    # 杀死进程组(包括子进程)
    if ps -p "$pid" > /dev/null 2>&1; then
        pkill -P "$pid" 2>/dev/null || true
        kill "$pid" 2>/dev/null || true
        sleep 1

        # 强制杀死
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi

    rm -f "$FRONTEND_PID"
    log_success "前端服务已停止"
}

# 停止后端
stop_backend() {
    if ! is_running "$BACKEND_PID"; then
        log_warn "后端服务未运行"
        return 1
    fi

    log_info "停止后端服务..."
    local pid=$(cat "$BACKEND_PID")

    # 杀死进程组(包括子进程)
    if ps -p "$pid" > /dev/null 2>&1; then
        pkill -P "$pid" 2>/dev/null || true
        kill "$pid" 2>/dev/null || true
        sleep 1

        # 强制杀死
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi

    rm -f "$BACKEND_PID"
    log_success "后端服务已停止"
}

# 显示状态
show_status() {
    echo "================== 服务状态 =================="

    if is_running "$FRONTEND_PID"; then
        echo -e "${GREEN}前端服务: 运行中${NC} (PID: $(cat $FRONTEND_PID), 端口: $FRONTEND_PORT)"
        echo "  访问地址: http://localhost:$FRONTEND_PORT"
    else
        echo -e "${RED}前端服务: 未运行${NC}"
    fi

    echo ""

    if is_running "$BACKEND_PID"; then
        echo -e "${GREEN}后端服务: 运行中${NC} (PID: $(cat $BACKEND_PID), 端口: $BACKEND_PORT)"
        echo "  API地址: http://localhost:$BACKEND_PORT"
        echo "  API文档: http://localhost:$BACKEND_PORT/docs"
    else
        echo -e "${RED}后端服务: 未运行${NC}"
    fi

    echo "============================================="
}

# 显示日志
show_logs() {
    local target=${1:-all}

    case $target in
        frontend)
            if [ -f "$FRONTEND_LOG" ]; then
                log_info "前端日志 (最后50行):"
                tail -n 50 "$FRONTEND_LOG"
            else
                log_warn "前端日志文件不存在"
            fi
            ;;
        backend)
            if [ -f "$BACKEND_LOG" ]; then
                log_info "后端日志 (最后50行):"
                tail -n 50 "$BACKEND_LOG"
            else
                log_warn "后端日志文件不存在"
            fi
            ;;
        all)
            show_logs frontend
            echo ""
            show_logs backend
            ;;
        *)
            log_error "未知的日志目标: $target"
            exit 1
            ;;
    esac
}

# 主逻辑
ACTION=${1:-help}
TARGET=${2:-all}

case $ACTION in
    start)
        case $TARGET in
            frontend)
                start_frontend
                ;;
            backend)
                start_backend
                ;;
            all)
                start_backend
                start_frontend
                echo ""
                show_status
                ;;
            *)
                log_error "未知的目标: $TARGET"
                log_info "可用目标: frontend, backend, all"
                exit 1
                ;;
        esac
        ;;

    stop)
        case $TARGET in
            frontend)
                stop_frontend
                ;;
            backend)
                stop_backend
                ;;
            all)
                stop_frontend
                stop_backend
                ;;
            *)
                log_error "未知的目标: $TARGET"
                log_info "可用目标: frontend, backend, all"
                exit 1
                ;;
        esac
        ;;

    restart)
        log_info "重启 $TARGET..."
        case $TARGET in
            frontend)
                stop_frontend || true
                sleep 1
                start_frontend
                ;;
            backend)
                stop_backend || true
                sleep 1
                start_backend
                ;;
            all)
                stop_frontend || true
                stop_backend || true
                sleep 1
                start_backend
                start_frontend
                echo ""
                show_status
                ;;
            *)
                log_error "未知的目标: $TARGET"
                log_info "可用目标: frontend, backend, all"
                exit 1
                ;;
        esac
        ;;

    status)
        show_status
        ;;

    logs)
        show_logs "$TARGET"
        ;;

    help|--help|-h)
        echo "Boss直聘自动化 - 启停控制脚本"
        echo ""
        echo "用法: ./manage.sh [命令] [目标]"
        echo ""
        echo "命令:"
        echo "  start    启动服务"
        echo "  stop     停止服务"
        echo "  restart  重启服务"
        echo "  status   查看服务状态"
        echo "  logs     查看日志"
        echo "  help     显示帮助信息"
        echo ""
        echo "目标:"
        echo "  frontend 前端服务"
        echo "  backend  后端服务"
        echo "  all      所有服务 (默认)"
        echo ""
        echo "示例:"
        echo "  ./manage.sh start all        # 启动所有服务"
        echo "  ./manage.sh stop backend     # 停止后端服务"
        echo "  ./manage.sh restart frontend # 重启前端服务"
        echo "  ./manage.sh status           # 查看服务状态"
        echo "  ./manage.sh logs backend     # 查看后端日志"
        echo ""
        echo "端口配置:"
        echo "  前端端口: $FRONTEND_PORT"
        echo "  后端端口: $BACKEND_PORT"
        echo "  配置文件: .ports"
        ;;

    *)
        log_error "未知的命令: $ACTION"
        echo "运行 './manage.sh help' 查看帮助"
        exit 1
        ;;
esac
