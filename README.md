# Boss 直聘自动化工具

基于 Playwright + FastAPI + React 的 Boss 直聘自动化招聘工具

## 功能特性

- ✅ 二维码登录（自动刷新、已登录检测）
- ✅ 自动化任务管理
- ✅ 候选人管理
- ✅ 消息模板管理
- ✅ 运行日志记录
- ✅ 系统配置

## 技术栈

### 后端
- Python 3.12
- FastAPI
- SQLModel + SQLite
- Playwright（浏览器自动化）
- uv（包管理器）

### 前端
- React 19
- TypeScript
- Vite 7
- Tailwind CSS 4
- shadcn/ui
- React Router v6

## 快速开始

### 方式 1: Mac 桌面版（推荐给普通用户）

**适用于：** 想直接使用的 Mac 用户，无需安装开发环境

查看 [electron-app/快速测试指南.md](electron-app/快速测试指南.md) 了解详情

```bash
# 开发模式测试（需要先启动后端和前端）
cd electron-app
./start-dev.sh

# 构建分发版本（生成 .dmg 安装包）
cd electron-app
npm run build
```

### 方式 2: Web 开发模式

**适用于：** 开发者，需要修改代码

#### 1. 安装依赖

```bash
# 后端
cd backend
uv sync

# 前端
cd frontend
npm install
```

#### 2. 启动服务

```bash
# 后端（端口 27421）
cd backend
uv run python -m app.main

# 前端（端口 13601）
cd frontend
npm run dev
```

#### 3. 访问应用

打开浏览器访问: http://localhost:13601

## 项目结构

```
Boss直聘自动化/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 入口文件
│   ├── pyproject.toml      # Python 依赖
│   └── uv.lock
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # UI 组件
│   │   ├── pages/          # 页面
│   │   ├── hooks/          # React Hooks
│   │   └── types/          # TypeScript 类型
│   └── package.json
├── electron-app/           # Mac 桌面版打包（新增）
│   ├── main.js            # Electron 主进程
│   ├── package.json       # Electron 配置
│   ├── scripts/           # 构建脚本
│   └── README.md          # 详细文档
└── README.md
```

## 主要功能

### 1. 登录管理
- 扫码登录
- 自动刷新二维码（最多5次）
- 已登录状态检测
- 用户信息展示

### 2. 任务管理
- 创建自动化任务
- 启动/暂停/取消任务
- 任务进度跟踪
- 任务历史记录

### 3. 候选人管理
- 候选人信息存储
- 状态管理
- 备注功能

### 4. 模板管理
- 消息模板创建
- 模板启用/禁用
- 使用统计

### 5. 运行日志
- 自动记录系统操作
- 日志级别筛选
- 操作类型筛选
- 分页查看

## 开发者

潘宇航

## 许可证

MIT
