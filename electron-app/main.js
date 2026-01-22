const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn, exec, execSync } = require('child_process');
const fs = require('fs');
const os = require('os');

let mainWindow;
let splashWindow;
let backendProcess;
let isQuitting = false;

// 后端服务配置
const BACKEND_PORT = 27421;
const FRONTEND_PORT = 13601;

// Playwright 浏览器缓存路径
const PLAYWRIGHT_CACHE_PATH = path.join(os.homedir(), 'Library', 'Caches', 'ms-playwright');

/**
 * 创建启动画面窗口
 */
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 400,
    height: 200,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    center: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  const splashHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          height: 100vh;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          padding: 20px;
        }
        .title { font-size: 24px; font-weight: 600; margin-bottom: 20px; }
        .status { font-size: 14px; opacity: 0.9; text-align: center; margin-bottom: 15px; }
        .progress-container {
          width: 100%;
          max-width: 300px;
          height: 6px;
          background: rgba(255,255,255,0.3);
          border-radius: 3px;
          overflow: hidden;
        }
        .progress-bar {
          height: 100%;
          background: white;
          border-radius: 3px;
          animation: loading 1.5s ease-in-out infinite;
          width: 30%;
        }
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
      </style>
    </head>
    <body>
      <div class="title">Boss直聘自动化</div>
      <div class="status" id="status">正在启动...</div>
      <div class="progress-container">
        <div class="progress-bar"></div>
      </div>
    </body>
    </html>
  `;

  splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHTML)}`);
}

/**
 * 更新启动画面状态
 */
function updateSplashStatus(message) {
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.webContents.executeJavaScript(
      `document.getElementById('status').textContent = '${message}';`
    );
  }
  console.log(`状态: ${message}`);
}

/**
 * 关闭启动画面
 */
function closeSplashWindow() {
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.close();
    splashWindow = null;
  }
}

/**
 * 检查 Playwright Chromium 是否已安装
 */
function isPlaywrightInstalled() {
  try {
    if (!fs.existsSync(PLAYWRIGHT_CACHE_PATH)) {
      return false;
    }

    const dirs = fs.readdirSync(PLAYWRIGHT_CACHE_PATH);
    // 查找 chromium 目录
    const chromiumDir = dirs.find(d => d.startsWith('chromium'));
    if (!chromiumDir) {
      return false;
    }

    const chromiumPath = path.join(PLAYWRIGHT_CACHE_PATH, chromiumDir);
    const contents = fs.readdirSync(chromiumPath);
    // 检查是否有实际的浏览器文件
    return contents.length > 0;
  } catch (error) {
    console.error('检查 Playwright 安装状态失败:', error);
    return false;
  }
}

/**
 * 递归复制目录
 */
function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
      // 保持可执行权限
      try {
        const stats = fs.statSync(srcPath);
        fs.chmodSync(destPath, stats.mode);
      } catch (e) {
        // 忽略权限错误
      }
    }
  }
}

/**
 * 安装 Playwright Chromium 浏览器
 */
function installPlaywright() {
  return new Promise((resolve, reject) => {
    updateSplashStatus('正在安装浏览器组件（首次启动需要）...');

    const isDev = !app.isPackaged;

    if (isDev) {
      // 开发模式：使用项目中的 playwright
      const backendPath = path.join(__dirname, '..', 'backend');
      const installProcess = spawn('uv', ['run', 'playwright', 'install', 'chromium'], {
        cwd: backendPath,
        env: { ...process.env }
      });

      installProcess.stdout.on('data', (data) => {
        console.log(`Playwright 安装: ${data}`);
        const output = data.toString();
        if (output.includes('Downloading')) {
          updateSplashStatus('正在下载浏览器组件...');
        } else if (output.includes('Installing')) {
          updateSplashStatus('正在安装浏览器组件...');
        }
      });

      installProcess.stderr.on('data', (data) => {
        console.error(`Playwright 安装错误: ${data}`);
      });

      installProcess.on('close', (code) => {
        if (code === 0) {
          console.log('Playwright Chromium 安装成功');
          resolve();
        } else {
          reject(new Error(`Playwright 安装失败，退出码: ${code}`));
        }
      });

      installProcess.on('error', (error) => {
        reject(error);
      });
    } else {
      // 生产模式：从应用资源目录复制浏览器
      try {
        updateSplashStatus('正在复制浏览器组件...');

        const bundledBrowsersPath = path.join(process.resourcesPath, 'app.asar.unpacked', 'backend-dist', 'playwright-browsers');

        if (!fs.existsSync(bundledBrowsersPath)) {
          reject(new Error('应用包中未包含浏览器组件，请重新下载安装包'));
          return;
        }

        // 查找 chromium 目录
        const dirs = fs.readdirSync(bundledBrowsersPath);
        const chromiumDir = dirs.find(d => d.startsWith('chromium'));

        if (!chromiumDir) {
          reject(new Error('应用包中未包含 Chromium 浏览器'));
          return;
        }

        const srcChromium = path.join(bundledBrowsersPath, chromiumDir);
        const destChromium = path.join(PLAYWRIGHT_CACHE_PATH, chromiumDir);

        // 确保目标目录存在
        fs.mkdirSync(PLAYWRIGHT_CACHE_PATH, { recursive: true });

        console.log(`正在复制浏览器: ${srcChromium} -> ${destChromium}`);
        copyDirRecursive(srcChromium, destChromium);

        console.log('Playwright Chromium 复制成功');
        resolve();
      } catch (error) {
        console.error('复制浏览器失败:', error);
        reject(error);
      }
    }
  });
}

/**
 * 确保 Playwright 浏览器已安装
 */
async function ensurePlaywrightInstalled() {
  if (isPlaywrightInstalled()) {
    console.log('Playwright Chromium 已安装');
    return;
  }

  console.log('Playwright Chromium 未安装，开始安装...');
  await installPlaywright();
}

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
      const backendPath = path.join(process.resourcesPath, 'app.asar.unpacked', 'backend-dist', 'backend');
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
    // 显示启动画面
    createSplashWindow();
    updateSplashStatus('正在初始化...');

    // 检查并安装 Playwright 浏览器（如果需要）
    updateSplashStatus('正在检查浏览器组件...');
    await ensurePlaywrightInstalled();

    // 启动后端服务
    updateSplashStatus('正在启动后端服务...');
    await startBackend();

    // 创建主窗口
    updateSplashStatus('正在加载界面...');
    createWindow();

    // 关闭启动画面
    closeSplashWindow();
  } catch (error) {
    console.error('应用启动失败:', error);
    closeSplashWindow();
    dialog.showErrorBox(
      '启动失败',
      '应用启动失败，请检查网络连接后重试。\n\n错误详情: ' + error.message
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
