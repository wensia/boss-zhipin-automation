# 启停脚本使用指南

## 脚本概述

`manage.sh` 是项目的统一启停控制脚本，提供了便捷的服务管理功能。

## 基本用法

```bash
./manage.sh [命令] [目标]
```

### 命令列表

| 命令 | 说明 |
|------|------|
| `start` | 启动服务 |
| `stop` | 停止服务 |
| `restart` | 重启服务 |
| `status` | 查看服务状态 |
| `logs` | 查看服务日志 |
| `help` | 显示帮助信息 |

### 目标列表

| 目标 | 说明 |
|------|------|
| `frontend` | 前端服务 |
| `backend` | 后端服务 |
| `all` | 所有服务 (默认) |

## 常用操作

### 1. 启动服务

**启动所有服务:**
```bash
./manage.sh start all
# 或简写
./manage.sh start
```

**仅启动前端:**
```bash
./manage.sh start frontend
```

**仅启动后端:**
```bash
./manage.sh start backend
```

### 2. 停止服务

**停止所有服务:**
```bash
./manage.sh stop all
# 或简写
./manage.sh stop
```

**仅停止前端:**
```bash
./manage.sh stop frontend
```

**仅停止后端:**
```bash
./manage.sh stop backend
```

### 3. 重启服务

**重启所有服务:**
```bash
./manage.sh restart all
# 或简写
./manage.sh restart
```

**仅重启前端:**
```bash
./manage.sh restart frontend
```

**仅重启后端:**
```bash
./manage.sh restart backend
```

### 4. 查看服务状态

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

### 5. 查看日志

**查看所有日志:**
```bash
./manage.sh logs all
# 或简写
./manage.sh logs
```

**仅查看前端日志:**
```bash
./manage.sh logs frontend
```

**仅查看后端日志:**
```bash
./manage.sh logs backend
```

## 端口配置

项目使用固定的不常用端口:

- **前端端口:** 13601
- **后端端口:** 27421

端口配置存储在项目根目录的 `.ports` 文件中:

```bash
# 项目端口配置
FRONTEND_PORT=13601
BACKEND_PORT=27421
```

如需修改端口，编辑 `.ports` 文件即可。脚本会自动读取新的端口配置。

## 日志文件

日志文件存储在 `logs/` 目录:

- **前端日志:** `logs/frontend.log`
- **后端日志:** `logs/backend.log`

## PID文件

进程ID文件存储在项目根目录:

- **前端PID:** `.frontend.pid`
- **后端PID:** `.backend.pid`

这些文件由脚本自动管理，无需手动操作。

## 典型工作流程

### 开发时

1. **启动所有服务**
   ```bash
   ./manage.sh start all
   ```

2. **开发过程中查看状态**
   ```bash
   ./manage.sh status
   ```

3. **查看日志排查问题**
   ```bash
   ./manage.sh logs backend
   ```

4. **修改代码后重启服务**
   ```bash
   ./manage.sh restart backend
   ```

5. **结束开发，停止所有服务**
   ```bash
   ./manage.sh stop all
   ```

### 调试时

1. **仅启动后端进行API测试**
   ```bash
   ./manage.sh start backend
   ```

2. **查看后端实时日志**
   ```bash
   ./manage.sh logs backend
   ```

3. **后端修改后快速重启**
   ```bash
   ./manage.sh restart backend
   ```

## 常见问题

### Q1: 启动失败怎么办?

A: 查看日志文件获取详细错误信息:
```bash
./manage.sh logs frontend
./manage.sh logs backend
```

### Q2: 端口被占用怎么办?

A: 检查是否有其他服务占用了13601或27421端口:
```bash
lsof -i :13601
lsof -i :27421
```

### Q3: 如何强制停止服务?

A: 脚本会自动尝试优雅停止和强制停止。如果还是无法停止，可以手动杀进程:
```bash
# 查看PID
cat .frontend.pid
cat .backend.pid

# 强制杀死进程
kill -9 <PID>

# 清理PID文件
rm .frontend.pid .backend.pid
```

### Q4: 前端依赖未安装怎么办?

A: 脚本会自动检测并安装前端依赖。如果需要手动安装:
```bash
cd frontend
npm install
```

### Q5: 后端虚拟环境不存在怎么办?

A: 脚本会提示虚拟环境不存在。手动初始化:
```bash
cd backend
uv sync
```

## 脚本特性

- ✅ **进程管理**: 使用PID文件跟踪进程
- ✅ **优雅停止**: 先尝试正常终止，失败后强制杀死
- ✅ **日志记录**: 所有输出重定向到日志文件
- ✅ **状态检查**: 实时显示服务运行状态
- ✅ **颜色输出**: 带颜色的控制台输出，清晰易读
- ✅ **错误处理**: 完善的错误提示和处理
- ✅ **自动检测**: 自动检测依赖是否安装

## 脚本位置

脚本位于项目根目录: `./manage.sh`

确保脚本有执行权限:
```bash
chmod +x manage.sh
```

## 获取帮助

随时运行帮助命令查看最新使用说明:
```bash
./manage.sh help
```
