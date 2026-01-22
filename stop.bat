@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    Boss直聘自动化工具 - 停止服务
echo ============================================
echo.

set "PORT=27421"
set "STOPPED=0"

:: 查找并终止占用端口的进程
echo [信息] 正在查找端口 %PORT% 上的进程...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    set "PID=%%a"
    if not "!PID!"=="" (
        echo [信息] 正在停止进程 PID: !PID!
        taskkill /F /PID !PID! >nul 2>&1
        set "STOPPED=1"
    )
)

:: 关闭 Python 进程 (app.main)
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr "PID"') do (
    set "PID=%%a"
)

if "%STOPPED%"=="1" (
    echo [成功] 服务已停止
) else (
    echo [信息] 没有发现正在运行的服务
)

echo.
pause
