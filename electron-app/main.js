const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;
let isQuitting = false;

// 后端服务配置
const BACKEND_PORT = 27421;
const FRONTEND_PORT = 13601;

/**
 * 强制终止进程及其所有子进程
 */
function killProcessTree(pid, signal = 'SIGTERM') {
  return new Promise((resolve) => {
    if (!pid) {
      resolve();
      return;
    }

    console.log(`正在终止进程树 PID: ${pid}`);

    if (process.platform === 'win32') {
      // Windows: 使用 taskkill
      exec(`taskkill /pid ${pid} /T /F`, (error) => {
        if (error) {
          console.error(`终止进程失败: ${error.message}`);
        }
        resolve();
      });
    } else {
      // macOS/Linux: 终止进程组
      try {
        // 发送信号给整个进程组（使用负数 PID）
        process.kill(-pid, signal);
        console.log(`已发送 ${signal} 信号给进程组 ${pid}`);

        // 等待 2 秒，如果还没终止则强制 SIGKILL
        setTimeout(() => {
          try {
            process.kill(-pid, 'SIGKILL');
            console.log(`已发送 SIGKILL 信号给进程组 ${pid}`);
          } catch (e) {
            // 进程可能已经终止
          }
          resolve();
        }, 2000);
      } catch (error) {
        if (error.code !== 'ESRCH') {
          // ESRCH 表示进程不存在，这是正常的
          console.error(`终止进程失败: ${error.message}`);
        }
        resolve();
      }
    }
  });
}

/**
 * 清理所有资源
 */
async function cleanupResources() {
  if (isQuitting) {
    return; // 避免重复清理
  }
  isQuitting = true;

  console.log('开始清理资源...');

  // 1. 关闭后端进程及其所有子进程（包括 Playwright/Chromium）
  if (backendProcess && backendProcess.pid) {
    console.log('正在终止后端服务及所有子进程...');
    await killProcessTree(backendProcess.pid, 'SIGTERM');
    backendProcess = null;
  }

  // 2. 额外保险：查找并终止所有相关的 chromium/playwright 进程
  if (process.platform !== 'win32') {
    exec('pkill -f "chromium|playwright"', (error) => {
      if (error && error.code !== 1) {
        // code 1 表示没有找到进程，这是正常的
        console.log('清理 chromium/playwright 进程');
      }
    });
  }

  // 3. 关闭所有窗口
  BrowserWindow.getAllWindows().forEach((win) => {
    if (!win.isDestroyed()) {
      win.destroy();
    }
  });

  console.log('资源清理完成');
}

/**
 * 启动后端服务
 */
function startBackend() {
  return new Promise((resolve, reject) => {
    const isDev = !app.isPackaged;

    if (isDev) {
      // 开发模式：使用 uv 运行
      console.log('启动开发模式后端...');
      const backendPath = path.join(__dirname, '..', 'backend');
      backendProcess = spawn('uv', ['run', 'python', '-m', 'app.main'], {
        cwd: backendPath,
        env: { ...process.env, PORT: BACKEND_PORT.toString() },
        detached: process.platform !== 'win32' // 在 Unix 系统上创建新的进程组
      });
    } else {
      // 生产模式：使用打包后的可执行文件
      console.log('启动生产模式后端...');
      const backendPath = path.join(process.resourcesPath, 'backend-dist', 'backend');
      backendProcess = spawn(backendPath, [], {
        env: { ...process.env, PORT: BACKEND_PORT.toString() },
        detached: process.platform !== 'win32' // 在 Unix 系统上创建新的进程组
      });
    }

    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('error', (error) => {
      console.error('后端启动失败:', error);
      reject(error);
    });

    backendProcess.on('exit', (code) => {
      console.log(`后端进程退出，代码: ${code}`);
    });

    // 等待后端启动
    setTimeout(() => {
      checkBackendHealth()
        .then(() => resolve())
        .catch(() => reject(new Error('后端健康检查失败')));
    }, 3000);
  });
}

/**
 * 检查后端健康状态
 */
async function checkBackendHealth() {
  const maxRetries = 10;
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(`http://localhost:${BACKEND_PORT}/api/health`);
      if (response.ok) {
        console.log('后端服务已就绪');
        return true;
      }
    } catch (error) {
      console.log(`等待后端启动... (${i + 1}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  throw new Error('后端启动超时');
}

/**
 * 创建主窗口
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    title: 'Boss直聘自动化工具',
    titleBarStyle: 'default',
    show: false
  });

  // 加载前端页面
  const isDev = !app.isPackaged;
  if (isDev) {
    // 开发模式：连接到 Vite 开发服务器
    mainWindow.loadURL(`http://localhost:${FRONTEND_PORT}`);
    // mainWindow.webContents.openDevTools();
  } else {
    // 生产模式：加载打包后的文件
    const frontendPath = path.join(__dirname, 'frontend-dist', 'index.html');
    mainWindow.loadFile(frontendPath);
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 窗口关闭时清理资源
  mainWindow.on('close', async (event) => {
    if (!isQuitting) {
      event.preventDefault();
      await cleanupResources();
      app.quit();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * 应用启动
 */
app.whenReady().then(async () => {
  try {
    // 启动后端服务
    await startBackend();

    // 创建窗口
    createWindow();
  } catch (error) {
    console.error('应用启动失败:', error);
    dialog.showErrorBox(
      '启动失败',
      '后端服务启动失败，请检查日志。\n错误: ' + error.message
    );
    app.quit();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

/**
 * 应用退出时清理
 */
app.on('window-all-closed', async () => {
  // Mac 上也要退出（不保持在 Dock 中）
  await cleanupResources();
  app.quit();
});

app.on('before-quit', async (event) => {
  if (!isQuitting) {
    event.preventDefault();
    await cleanupResources();
    app.quit();
  }
});

// 处理应用被强制终止的情况
app.on('will-quit', async (event) => {
  if (!isQuitting) {
    event.preventDefault();
    await cleanupResources();
    process.exit(0);
  }
});

/**
 * 异常处理
 */
process.on('uncaughtException', async (error) => {
  console.error('未捕获的异常:', error);
  await cleanupResources();
  process.exit(1);
});

process.on('unhandledRejection', async (reason, promise) => {
  console.error('未处理的 Promise 拒绝:', reason);
  await cleanupResources();
  process.exit(1);
});

// 处理 SIGINT (Ctrl+C) 和 SIGTERM
process.on('SIGINT', async () => {
  console.log('收到 SIGINT 信号');
  await cleanupResources();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('收到 SIGTERM 信号');
  await cleanupResources();
  process.exit(0);
});
