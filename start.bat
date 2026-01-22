@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    Boss直聘自动化工具 - 启动中...
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "PID_FILE=%SCRIPT_DIR%.backend.pid"
set "PORT=27421"

:: 检查端口是否被占用
netstat -ano | findstr ":%PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 端口 %PORT% 已被占用
    echo [信息] 如需停止已有服务，请运行: stop.bat
    echo [信息] 正在打开浏览器...
    start http://localhost:%PORT%
    pause
    exit /b 0
)

:: 确保 uv 可用
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 uv，请先运行 install.bat
    pause
    exit /b 1
)

cd /d "%BACKEND_DIR%"

:: 检查虚拟环境
if not exist ".venv" (
    echo [信息] 首次运行，正在安装依赖...
    uv sync
    
    echo [信息] 正在安装 Playwright 浏览器...
    uv run playwright install chromium
)

echo.
echo ============================================
echo [成功] 访问地址: http://localhost:%PORT%
echo ============================================
echo.
echo [信息] 关闭此窗口或按 Ctrl+C 停止服务
echo.

:: 延迟打开浏览器
timeout /t 2 /nobreak >nul
start http://localhost:%PORT%

:: 启动后端服务 (前台运行)
uv run python -m app.main
