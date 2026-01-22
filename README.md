# Boss 直聘自动化工具

基于 Playwright + FastAPI + React 的 Boss 直聘自动化招聘工具

## 功能特性

- 二维码登录（自动刷新、已登录检测）
- 多账号管理（支持切换不同招聘账号）
- 职位筛选（年龄、学历、经验等条件过滤）
- 自动打招呼（批量发送招呼消息）
- 消息模板管理
- 运行日志记录
- 系统配置

## 系统要求

### macOS
- macOS 10.15 或更高版本
- 终端 (Terminal)
- 网络连接（首次安装需要下载依赖）

### Windows
- Windows 10 或更高版本
- PowerShell（Windows 自带）
- 网络连接（首次安装需要下载依赖）

> **注意**: 首次运行会自动安装所需的 Python 环境和浏览器组件，请保持网络连接。

## 快速开始

### macOS 用户

```bash
# 1. 解压文件后，打开终端进入项目目录
cd Boss直聘自动化

# 2. 首次运行，设置执行权限
chmod +x install.sh start.sh stop.sh

# 3. 首次安装（只需运行一次）
./install.sh

# 4. 启动应用
./start.sh

# 5. 停止应用
./stop.sh
```

### Windows 用户

```powershell
# 1. 解压文件后，在文件夹中右键选择"在终端中打开"

# 2. 首次安装（只需运行一次）
.\install.bat

# 3. 启动应用
.\start.bat

# 4. 停止应用
.\stop.bat
```

### 访问应用

启动后自动打开浏览器访问: **http://localhost:27421**

如果浏览器没有自动打开，请手动复制上面的地址到浏览器打开。

## 使用流程

### 1. 初始化浏览器
- 进入"自动化向导"页面
- 可选择是否显示浏览器窗口（建议首次使用时显示，便于观察）
- 点击"开始初始化"

### 2. 登录账号
- **已有账号**: 选择之前登录过的账号直接使用
- **新账号**: 使用 Boss 直聘 APP 扫描二维码登录

### 3. 选择职位
- 从已发布的职位列表中选择要招聘的职位

### 4. 配置筛选条件
- 设置候选人筛选条件（年龄、学历、工作经验等）
- 设置打招呼消息模板

### 5. 启动任务
- 确认配置后开始自动化任务
- 可在"任务列表"页面查看进度

## 常见问题

### Q: 端口被占用怎么办？

**macOS:**
```bash
# 查看占用端口的进程
lsof -i :27421

# 结束进程
kill -9 <PID>

# 或者直接运行停止脚本
./stop.sh
```

**Windows:**
```powershell
# 查看占用端口的进程
netstat -ano | findstr :27421

# 结束进程
taskkill /F /PID <PID>

# 或者直接运行停止脚本
.\stop.bat
```

### Q: 浏览器窗口不显示？

1. 确保勾选了"显示浏览器窗口"选项
2. 使用 `Cmd+Tab` (Mac) 或 `Alt+Tab` (Windows) 切换窗口
3. 如果问题持续，尝试重新安装 Playwright 浏览器：

```bash
# macOS
cd backend && source .venv/bin/activate && playwright install chromium

# Windows
cd backend && .venv\Scripts\activate && playwright install chromium
```

### Q: 页面打不开？

1. 确认终端显示"访问地址: http://localhost:27421"后再打开浏览器
2. 检查是否有防火墙阻止了本地连接
3. 尝试使用 http://127.0.0.1:27421 访问

### Q: 安装依赖失败？

1. 检查网络连接
2. 如果在中国大陆，可能需要配置镜像源
3. 尝试多次运行安装脚本

### Q: 二维码一直刷新？

1. 二维码有效期约 2 分钟，系统会自动刷新最多 5 次
2. 请在二维码显示后尽快使用 Boss 直聘 APP 扫码
3. 如果超过 5 次，点击"重新登录"按钮

## 项目结构

```
Boss直聘自动化/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 入口文件
│   ├── data/               # 数据存储
│   └── pyproject.toml      # Python 依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # UI 组件
│   │   ├── pages/          # 页面
│   │   └── hooks/          # React Hooks
│   └── dist/               # 构建产物
├── install.sh              # macOS 安装脚本
├── start.sh                # macOS 启动脚本
├── stop.sh                 # macOS 停止脚本
├── install.bat             # Windows 安装脚本
├── start.bat               # Windows 启动脚本
├── stop.bat                # Windows 停止脚本
└── 使用说明.txt             # 快速使用说明
```

## 技术栈

### 后端
- Python 3.12+
- FastAPI
- SQLModel + SQLite
- Playwright（浏览器自动化）

### 前端
- React 19
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

## 许可证

MIT License

## 开发者

潘宇航
