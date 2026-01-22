@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    Boss直聘自动化工具 - Windows 首次安装
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

:: ============================================
:: 步骤 1: 安装 uv (Python 包管理器)
:: ============================================
echo [1/4] 检查 uv (Python 包管理器)...

where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] uv 已安装
) else (
    echo [信息] 正在安装 uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    :: 刷新环境变量
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    
    where uv >nul 2>&1
    if %errorlevel% equ 0 (
        echo [成功] uv 安装成功
    ) else (
        echo [错误] uv 安装失败，请手动安装: https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
)

:: ============================================
:: 步骤 2: 安装后端依赖
:: ============================================
echo.
echo [2/4] 安装后端依赖...

cd /d "%BACKEND_DIR%"

uv sync
if %errorlevel% neq 0 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)
echo [成功] 后端依赖安装成功

:: ============================================
:: 步骤 3: 安装 Playwright 浏览器
:: ============================================
echo.
echo [3/4] 安装 Playwright 浏览器 (Chromium)...
echo [信息] 这可能需要几分钟，请耐心等待...

uv run playwright install chromium
if %errorlevel% neq 0 (
    echo [警告] Playwright 浏览器安装可能不完整
) else (
    echo [成功] Playwright Chromium 安装成功
)

:: ============================================
:: 步骤 4: 检查前端构建
:: ============================================
echo.
echo [4/4] 检查前端构建...

cd /d "%FRONTEND_DIR%"

if exist "dist\index.html" (
    echo [成功] 前端已构建完成
) else (
    echo [信息] 前端未构建，检查 Node.js...
    
    where node >nul 2>&1
    if %errorlevel% equ 0 (
        echo [信息] 正在构建前端...
        call npm install
        call npm run build
        
        if exist "dist\index.html" (
            echo [成功] 前端构建成功
        ) else (
            echo [错误] 前端构建失败
            pause
            exit /b 1
        )
    ) else (
        echo [警告] 未检测到 Node.js，跳过前端构建
        echo [信息] 如需重新构建前端，请先安装 Node.js: https://nodejs.org/
    )
)

:: ============================================
:: 安装完成
:: ============================================
echo.
echo ============================================
echo [成功] 安装完成!
echo ============================================
echo.
echo [信息] 现在可以运行 start.bat 启动应用
echo.
echo [信息] 访问地址: http://localhost:27421
echo.

pause
