# Boss直聘自动化项目初始化文档

## 项目概述

本项目是一个Boss直聘自动化工具,采用前后端分离架构。

### 技术栈

**前端:**
- **Vite + React** - 现代化前端构建工具和框架
- **Tailwind CSS** - 实用优先的CSS框架
- **shadcn/ui** - 高质量可复用的React组件库
- **Lucide React** - 官方推荐的图标库
- **静态文件部署** - 无需前端服务器,构建后直接使用静态文件

**后端:**
- **uv** - 现代化的Python包管理器
- **FastAPI** - 高性能异步Web框架
- **SQLModel** - 结合SQLAlchemy和Pydantic的ORM
- **SQLite** - 轻量级数据库

---

## 前端初始化

### 1. 创建Vite + React项目

```bash
# 使用Vite创建React + TypeScript项目
npm create vite@latest frontend -- --template react-ts

cd frontend
npm install
```

### 2. 安装Tailwind CSS

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**配置 `tailwind.config.js`:**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**在 `src/index.css` 中添加Tailwind指令:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 3. 安装shadcn/ui

```bash
# 安装shadcn/ui CLI
npx shadcn@latest init
```

在初始化过程中选择:
- Style: Default
- Base color: 根据需求选择
- CSS variables: Yes

**安装常用组件示例:**

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add table
npx shadcn@latest add dialog
npx shadcn@latest add toast
```

### 4. 安装Lucide React图标库

```bash
npm install lucide-react
```

**使用示例:**

```tsx
import { Menu, X, Search } from 'lucide-react'

function App() {
  return (
    <div>
      <Menu size={24} />
      <Search size={20} color="blue" />
    </div>
  )
}
```

### 5. 构建静态文件

```bash
# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

构建后的静态文件位于 `frontend/dist` 目录,可直接部署或通过后端静态文件服务提供。

---

## 后端初始化

### 1. 安装uv

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 创建Python项目

```bash
# 创建后端目录
mkdir backend
cd backend

# 初始化uv项目
uv init
```

### 3. 安装依赖

```bash
# 添加FastAPI和相关依赖
uv add fastapi
uv add "uvicorn[standard]"
uv add sqlmodel
uv add aiosqlite  # 异步SQLite支持

# 开发依赖
uv add --dev pytest
uv add --dev black
uv add --dev ruff
```

### 4. 创建项目结构

```bash
mkdir -p backend/app/{models,routes,services}
touch backend/app/__init__.py
touch backend/app/main.py
touch backend/app/database.py
touch backend/app/models/__init__.py
touch backend/app/routes/__init__.py
touch backend/app/services/__init__.py
```

### 5. 基础代码示例

**`backend/app/main.py`:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源

app = FastAPI(
    title="Boss直聘自动化API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载前端静态文件(构建后)
# app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# 导入路由
# from app.routes import xxx
# app.include_router(xxx.router)
```

**`backend/app/database.py`:**

```python
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./database.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 开发时启用SQL日志
    future=True
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
```

**模型示例 `backend/app/models/example.py`:**

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class JobBase(SQLModel):
    title: str
    company: str
    salary: str
    location: str
    description: Optional[str] = None

class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class JobCreate(JobBase):
    pass

class JobRead(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime
```

### 6. 运行后端服务

```bash
# 开发模式(热重载) - 使用环境变量中配置的端口
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 27421

# 或者使用FastAPI CLI
uv run fastapi dev app/main.py

# 或者直接运行(会从.env读取端口)
uv run python -m app.main
```

---

## 项目结构

```
Boss直聘自动化/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── lib/             # shadcn/ui配置和工具
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/                  # 后端项目
│   ├── app/
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # API路由
│   │   ├── services/        # 业务逻辑
│   │   ├── database.py      # 数据库配置
│   │   └── main.py          # 应用入口
│   ├── tests/               # 测试文件
│   ├── .env                 # 环境变量配置
│   ├── .env.example         # 环境变量模板
│   ├── pyproject.toml       # uv项目配置
│   ├── uv.lock              # 依赖锁文件
│   └── database.db          # SQLite数据库
│
├── .gitignore               # Git忽略规则
├── .ports                   # 端口配置文件
├── manage.sh                # 启停控制脚本
├── PROJECT_INIT.md          # 本文档
└── README.md                # 主README文档
```

---

## 开发工作流

### 使用启停脚本 (推荐)

如果已创建启停脚本(参考上一章节)，使用以下命令:

```bash
# 启动所有服务
./manage.sh start all

# 访问应用
# 前端: http://localhost:13601
# 后端API: http://localhost:27421
# API文档: http://localhost:27421/docs

# 查看状态
./manage.sh status

# 停止所有服务
./manage.sh stop all
```

### 手动启动 (不推荐)

**前端开发:**

```bash
cd frontend
npm run dev
# 访问 http://localhost:13601
```

**后端开发:**

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 27421
# API文档: http://localhost:27421/docs
```

### 生产部署

1. **构建前端:**
   ```bash
   cd frontend
   npm run build
   ```

2. **配置后端静态文件服务:**
   在 `backend/app/main.py` 中取消注释:
   ```python
   app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
   ```

3. **运行后端:**
   ```bash
   cd backend
   uv run uvicorn app.main:app --host 0.0.0.0 --port 27421
   ```

4. **访问应用:**
   打开浏览器访问 `http://localhost:27421`

---

## 创建启停管理脚本

为了方便开发和管理服务，建议创建统一的启停控制脚本。

### 1. 配置端口

首先创建端口配置文件 `.ports`，使用不常用的随机端口避免冲突:

```bash
# 在项目根目录创建 .ports 文件
cat > .ports << 'EOF'
# 项目端口配置
# 此文件在首次创建启停脚本时生成，请勿随意修改

FRONTEND_PORT=13601
BACKEND_PORT=27421
EOF
```

**端口说明:**
- 前端使用 10000-19999 范围的端口
- 后端使用 20000-29999 范围的端口
- 避免使用常用端口(如 3000, 5000, 8000 等)

### 2. 配置前端端口

**更新 `frontend/vite.config.ts`:**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 13601,  // 使用固定端口
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:27421',  // 后端API地址
        changeOrigin: true,
      },
    },
  },
})
```

**创建 `frontend/.env`:**

```bash
cat > frontend/.env << 'EOF'
# 前端环境变量配置

# API基础URL (开发环境使用代理，生产环境需要修改)
VITE_API_BASE_URL=/api

# 后端API端口 (开发时用于代理配置)
VITE_BACKEND_PORT=27421
EOF
```

### 3. 配置后端端口

**创建 `backend/.env`:**

```bash
cat > backend/.env << 'EOF'
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./database.db

# API配置
API_HOST=0.0.0.0
API_PORT=27421
DEBUG=True

# CORS配置
ALLOWED_ORIGINS=*

# Boss直聘配置
BOSS_USERNAME=
BOSS_PASSWORD=
EOF
```

**更新 `backend/app/main.py` 的启动代码:**

```python
if __name__ == "__main__":
    import uvicorn
    import os

    # 从环境变量读取端口配置，默认使用27421
    port = int(os.getenv("API_PORT", 27421))
    host = os.getenv("API_HOST", "0.0.0.0")

    uvicorn.run("app.main:app", host=host, port=port, reload=True)
```

### 4. 创建启停脚本

创建 `manage.sh` 脚本用于统一管理服务:

```bash
cat > manage.sh << 'SCRIPT_EOF'
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
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

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

    if [ ! -d "node_modules" ]; then
        log_info "检测到未安装依赖，正在安装..."
        npm install
    fi

    nohup npm run dev -- --port "$FRONTEND_PORT" --host 0.0.0.0 > "$FRONTEND_LOG" 2>&1 &
    echo $! > "$FRONTEND_PID"

    sleep 2
    if is_running "$FRONTEND_PID"; then
        log_success "前端服务启动成功"
        log_info "访问地址: http://localhost:$FRONTEND_PORT"
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

    if [ ! -d ".venv" ]; then
        log_error "虚拟环境不存在，请先运行 'cd backend && uv sync'"
        return 1
    fi

    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi

    nohup uv run uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload > "$BACKEND_LOG" 2>&1 &
    echo $! > "$BACKEND_PID"

    sleep 2
    if is_running "$BACKEND_PID"; then
        log_success "后端服务启动成功"
        log_info "API地址: http://localhost:$BACKEND_PORT"
        log_info "API文档: http://localhost:$BACKEND_PORT/docs"
    else
        log_error "后端服务启动失败，请查看日志: $BACKEND_LOG"
        return 1
    fi
}

# 停止服务
stop_service() {
    local pid_file=$1
    local service_name=$2

    if ! is_running "$pid_file"; then
        log_warn "${service_name}服务未运行"
        return 1
    fi

    log_info "停止${service_name}服务..."
    local pid=$(cat "$pid_file")

    if ps -p "$pid" > /dev/null 2>&1; then
        pkill -P "$pid" 2>/dev/null || true
        kill "$pid" 2>/dev/null || true
        sleep 1
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi

    rm -f "$pid_file"
    log_success "${service_name}服务已停止"
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

# 主逻辑
ACTION=${1:-help}
TARGET=${2:-all}

case $ACTION in
    start)
        case $TARGET in
            frontend) start_frontend ;;
            backend) start_backend ;;
            all)
                start_backend
                start_frontend
                echo ""
                show_status
                ;;
            *) log_error "未知的目标: $TARGET"; exit 1 ;;
        esac
        ;;
    stop)
        case $TARGET in
            frontend) stop_service "$FRONTEND_PID" "前端" ;;
            backend) stop_service "$BACKEND_PID" "后端" ;;
            all)
                stop_service "$FRONTEND_PID" "前端" || true
                stop_service "$BACKEND_PID" "后端" || true
                ;;
            *) log_error "未知的目标: $TARGET"; exit 1 ;;
        esac
        ;;
    restart)
        log_info "重启 $TARGET..."
        case $TARGET in
            frontend)
                stop_service "$FRONTEND_PID" "前端" || true
                sleep 1
                start_frontend
                ;;
            backend)
                stop_service "$BACKEND_PID" "后端" || true
                sleep 1
                start_backend
                ;;
            all)
                stop_service "$FRONTEND_PID" "前端" || true
                stop_service "$BACKEND_PID" "后端" || true
                sleep 1
                start_backend
                start_frontend
                echo ""
                show_status
                ;;
            *) log_error "未知的目标: $TARGET"; exit 1 ;;
        esac
        ;;
    status) show_status ;;
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
        ;;
    *) log_error "未知的命令: $ACTION"; echo "运行 './manage.sh help' 查看帮助"; exit 1 ;;
esac
SCRIPT_EOF

# 添加执行权限
chmod +x manage.sh
```

### 5. 更新 .gitignore

在 `.gitignore` 中添加脚本运行时生成的文件:

```bash
# 在现有的 .gitignore 中添加
echo "" >> .gitignore
echo "# Process Management" >> .gitignore
echo "*.pid" >> .gitignore
echo "pids/" >> .gitignore
echo "run.log" >> .gitignore
echo "" >> .gitignore
echo "# Logs" >> .gitignore
echo "logs/" >> .gitignore
```

### 6. 使用脚本

**启动所有服务:**
```bash
./manage.sh start all
```

**查看状态:**
```bash
./manage.sh status
```

输出示例:
```
================== 服务状态 ==================
前端服务: 运行中 (PID: 12345, 端口: 13601)
  访问地址: http://localhost:13601

后端服务: 运行中 (PID: 12346, 端口: 27421)
  API地址: http://localhost:27421
  API文档: http://localhost:27421/docs
=============================================
```

**停止所有服务:**
```bash
./manage.sh stop all
```

**重启特定服务:**
```bash
./manage.sh restart backend
```

### 7. 脚本特性

- ✅ **进程管理**: 使用PID文件跟踪进程
- ✅ **优雅停止**: 先尝试正常终止，失败后强制杀死
- ✅ **日志记录**: 所有输出重定向到 `logs/` 目录
- ✅ **状态检查**: 实时显示服务运行状态
- ✅ **颜色输出**: 带颜色的控制台输出，清晰易读
- ✅ **错误处理**: 完善的错误提示和处理
- ✅ **自动检测**: 自动检测依赖是否安装

### 8. 常见问题

**Q: 启动失败怎么办?**

A: 查看日志文件:
```bash
tail -f logs/frontend.log  # 查看前端日志
tail -f logs/backend.log   # 查看后端日志
```

**Q: 端口被占用怎么办?**

A: 修改 `.ports` 文件中的端口号，然后更新配置文件:
- `frontend/vite.config.ts` 中的 `server.port` 和 `server.proxy.target`
- `frontend/.env` 中的 `VITE_BACKEND_PORT`
- `backend/.env` 中的 `API_PORT`

**Q: 如何添加日志查看功能?**

A: 在 `manage.sh` 中添加 `logs` 命令:
```bash
case $ACTION in
    logs)
        case $TARGET in
            frontend) tail -n 50 "$FRONTEND_LOG" ;;
            backend) tail -n 50 "$BACKEND_LOG" ;;
            all)
                echo "=== 前端日志 ==="
                tail -n 25 "$FRONTEND_LOG"
                echo ""
                echo "=== 后端日志 ==="
                tail -n 25 "$BACKEND_LOG"
                ;;
        esac
        ;;
esac
```

---

## 常用命令参考

### 前端

```bash
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览构建结果
npm run lint         # 代码检查
```

### 后端

```bash
uv add <package>           # 添加依赖
uv remove <package>        # 移除依赖
uv run <command>           # 运行命令
uv sync                    # 同步依赖
uv run pytest              # 运行测试
uv run black .             # 代码格式化
uv run ruff check .        # 代码检查
```

---

## 启停脚本快速参考

如果已按上述步骤创建了 `manage.sh` 脚本，可使用以下命令:

### 基本命令

| 命令 | 说明 |
|------|------|
| `./manage.sh start all` | 启动所有服务 |
| `./manage.sh stop all` | 停止所有服务 |
| `./manage.sh restart all` | 重启所有服务 |
| `./manage.sh status` | 查看服务状态 |
| `./manage.sh help` | 显示帮助信息 |

### 单独控制

| 命令 | 说明 |
|------|------|
| `./manage.sh start frontend` | 仅启动前端 |
| `./manage.sh start backend` | 仅启动后端 |
| `./manage.sh stop frontend` | 仅停止前端 |
| `./manage.sh restart backend` | 仅重启后端 |

### 访问地址

- **前端:** http://localhost:13601
- **后端API:** http://localhost:27421
- **API文档:** http://localhost:27421/docs

### 日志文件

- **前端日志:** `logs/frontend.log`
- **后端日志:** `logs/backend.log`

查看日志:
```bash
tail -f logs/frontend.log  # 实时查看前端日志
tail -f logs/backend.log   # 实时查看后端日志
```

---

## 版本信息

所有依赖均使用最新稳定版本(截至文档创建时间)。

可通过以下命令检查当前版本:

```bash
# 前端
npm list --depth=0

# 后端
uv pip list
```

---

## 下一步

完成初始化后，建议按以下顺序进行开发:

1. **创建启停脚本** (推荐，提高开发效率)
   - 参考"创建启停管理脚本"章节
   - 配置端口和环境变量
   - 测试脚本功能

2. **设计数据库模型**
   - 在 `backend/app/models/` 中定义数据模型
   - 使用SQLModel创建表结构

3. **实现API路由**
   - 在 `backend/app/routes/` 中实现API端点
   - 在 `backend/app/main.py` 中注册路由

4. **开发前端界面**
   - 使用shadcn/ui组件构建界面
   - 使用Lucide React图标
   - 通过 `/api` 代理调用后端接口

5. **实现Boss直聘自动化核心功能**
   - 在 `backend/app/services/` 中实现业务逻辑
   - 集成自动化爬虫或API调用

6. **添加测试覆盖**
   - 使用pytest编写后端测试
   - 运行 `uv run pytest`

7. **配置CI/CD流程**
   - 配置GitHub Actions或其他CI工具
   - 自动化测试和部署

---

## 参考文档

- [Vite](https://vitejs.dev/)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Lucide Icons](https://lucide.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [uv](https://docs.astral.sh/uv/)
