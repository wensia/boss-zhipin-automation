# Boss直聘自动化 - Mac 桌面版

这是一个基于 Electron 的 Mac 桌面应用打包方案，可以将 Boss直聘自动化工具打包成独立的 `.app` 和 `.dmg` 文件分享给其他 Mac 用户。

## 🔒 安全特性

**强制进程清理机制** - 防止内存溢出

- ✅ 关闭窗口时自动终止所有子进程（Python、Playwright、Chromium）
- ✅ 多层清理保障，确保浏览器进程完全退出
- ✅ 防止内存泄漏和资源耗尽
- ✅ 处理异常退出和崩溃情况

详见：[进程管理说明.md](./进程管理说明.md)

## 📋 目录结构

```
electron-app/
├── main.js              # Electron 主进程
├── preload.js           # 预加载脚本
├── package.json         # Electron 配置
├── scripts/             # 构建脚本
│   └── build-backend.js # 后端打包脚本
├── assets/              # 资源文件
│   └── icon.icns       # 应用图标（需要自己添加）
├── frontend-dist/       # 前端构建产物（自动生成）
├── backend-dist/        # 后端构建产物（自动生成）
└── dist/                # 最终打包文件（自动生成）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd electron-app
npm install
```

### 2. 开发模式测试

在开发模式下，Electron 会连接到你现有的前后端服务，不会影响正常开发。

**前提条件：**
- 后端服务运行在 `http://localhost:27421`
- 前端服务运行在 `http://localhost:13601`

```bash
# 终端 1：启动后端（在 backend 目录）
cd ../backend
uv run python -m app.main

# 终端 2：启动前端（在 frontend 目录）
cd ../frontend
npm run dev

# 终端 3：启动 Electron（在 electron-app 目录）
cd electron-app
npm start
```

这样会打开一个桌面应用窗口，显示你的前端界面。

### 3. 构建生产版本

#### 3.1 准备应用图标（可选）

将 `icon.icns` 文件放到 `assets/` 目录下。如果没有图标，可以跳过此步骤，使用默认图标。

**制作图标：**
```bash
# 方法1：使用在线工具
# 访问 https://cloudconvert.com/png-to-icns
# 上传 1024x1024 的 PNG 图片，转换为 ICNS

# 方法2：使用命令行（需要 iconutil）
mkdir icon.iconset
# 准备不同尺寸的图片...
iconutil -c icns icon.iconset -o assets/icon.icns
```

#### 3.2 添加 PyInstaller 依赖

在后端项目中添加 PyInstaller：

```bash
cd ../backend
uv add pyinstaller --dev
```

#### 3.3 构建应用

```bash
cd electron-app
npm run build
```

这个命令会：
1. 构建前端（React + Vite）
2. 打包后端（Python + PyInstaller）
3. 打包 Electron 应用
4. 生成 `.dmg` 安装文件

#### 3.4 查看结果

构建完成后，在 `dist/` 目录下可以找到：
- `Boss直聘自动化-1.0.0-arm64.dmg` (Apple Silicon)
- `Boss直聘自动化-1.0.0-x64.dmg` (Intel)
- `Boss直聘自动化.app` (应用程序)

## 📦 分享给他人

### 方法 1：分享 DMG 文件（推荐）

```bash
# 将 DMG 文件发送给其他人
# 用户只需双击安装即可
dist/Boss直聘自动化-1.0.0-arm64.dmg
```

### 方法 2：分享 APP 文件

```bash
# 压缩 .app 文件
cd dist/mac-arm64  # 或 mac-x64
zip -r Boss直聘自动化.zip "Boss直聘自动化.app"
```

## 🔧 开发说明

### 端口配置

- 后端端口: `27421`
- 前端端口: `13601`

如需修改端口，请在 `main.js` 中修改：

```javascript
const BACKEND_PORT = 27421;
const FRONTEND_PORT = 13601;
```

### 打包配置

打包配置在 `package.json` 的 `build` 字段中：

```json
{
  "build": {
    "appId": "com.boss.automation",
    "productName": "Boss直聘自动化",
    "mac": {
      "category": "public.app-category.productivity",
      "target": ["dmg"]
    }
  }
}
```

### 后端打包

后端使用 PyInstaller 打包成单文件可执行程序。如果遇到依赖问题，可以在 `scripts/build-backend.js` 中添加 `--hidden-import` 选项。

### 前端构建

前端使用 Vite 构建，输出到 `frontend-dist/` 目录。如需修改前端 API 地址，请确保指向 `http://localhost:27421`。

## 🐛 常见问题

### Q1: 后端启动失败

**解决方法：**
1. 检查 `backend-dist/backend` 是否存在
2. 检查后端依赖是否完整
3. 查看终端日志中的错误信息

### Q2: 前端页面无法加载

**解决方法：**
1. 检查 `frontend-dist/index.html` 是否存在
2. 确保前端已正确构建：`npm run build:frontend`

### Q3: 打包后体积过大

**原因：** Electron 应用通常较大（100-200MB），这是正常的。

**优化方法：**
- 使用 `asar` 压缩资源文件
- 移除不必要的依赖
- 考虑使用 Tauri（更轻量，但需要 Rust）

### Q4: Mac 安全提示无法打开

**解决方法：**
```bash
# 右键点击应用，选择"打开"
# 或在终端中执行：
xattr -cr "/Applications/Boss直聘自动化.app"
```

对于分发给他人，需要进行代码签名：
```bash
# 需要 Apple Developer 账号
codesign --deep --force --sign "Developer ID" "Boss直聘自动化.app"
```

### Q5: 开发模式下连接不到服务

**检查清单：**
- [ ] 后端服务是否在 `localhost:27421` 运行？
- [ ] 前端服务是否在 `localhost:13601` 运行？
- [ ] 防火墙是否阻止了连接？

## 📝 开发模式 vs 生产模式

| 特性 | 开发模式 | 生产模式 |
|------|---------|---------|
| 前端 | 连接到 Vite Dev Server | 加载本地打包文件 |
| 后端 | 使用 `uv run python` | 使用 PyInstaller 可执行文件 |
| 热重载 | ✅ 支持 | ❌ 不支持 |
| 打包大小 | - | ~150MB |
| 依赖 | 需要 Python/Node.js | 无需任何依赖 |

## 🎯 下一步

1. **测试应用**
   ```bash
   npm start  # 开发模式测试
   ```

2. **构建生产版本**
   ```bash
   npm run build
   ```

3. **分享给朋友**
   - 发送 `dist/` 目录下的 `.dmg` 文件
   - 告诉他们双击安装即可

## 📞 支持

如有问题，请检查：
1. Node.js 版本 >= 18
2. Python 版本 >= 3.12
3. 所有依赖已安装
4. 前后端服务可以正常运行

## 📄 许可证

MIT

---

**注意：** 此 Electron 版本是独立的打包方案，不会影响原项目的正常开发和运行。
