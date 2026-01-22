const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('开始构建后端...');

const backendDir = path.join(__dirname, '..', '..', 'backend');
const outputDir = path.join(__dirname, '..', 'backend-dist');

// 清理输出目录
if (fs.existsSync(outputDir)) {
  fs.rmSync(outputDir, { recursive: true });
}
fs.mkdirSync(outputDir, { recursive: true });

try {
  // 使用 PyInstaller 打包后端
  console.log('使用 PyInstaller 打包后端...');

  const pyinstallerCmd = `
    cd "${backendDir}" && \
    uv run pyinstaller \
      --name=backend \
      --onefile \
      --distpath="${outputDir}" \
      --workpath="${path.join(outputDir, 'build')}" \
      --specpath="${outputDir}" \
      --hidden-import=uvicorn.logging \
      --hidden-import=uvicorn.loops \
      --hidden-import=uvicorn.loops.auto \
      --hidden-import=uvicorn.protocols \
      --hidden-import=uvicorn.protocols.http \
      --hidden-import=uvicorn.protocols.http.auto \
      --hidden-import=uvicorn.protocols.websockets \
      --hidden-import=uvicorn.protocols.websockets.auto \
      --hidden-import=uvicorn.lifespan \
      --hidden-import=uvicorn.lifespan.on \
      --collect-all=playwright \
      --collect-all=fastapi \
      --collect-all=sqlmodel \
      --collect-all=aiosqlite \
      --hidden-import=aiosqlite \
      app/main.py
  `.replace(/\n\s+/g, ' ');

  execSync(pyinstallerCmd, { stdio: 'inherit' });

  // 复制数据库和其他必要文件
  const filesToCopy = ['database.db'];
  filesToCopy.forEach(file => {
    const srcPath = path.join(backendDir, file);
    const destPath = path.join(outputDir, file);
    if (fs.existsSync(srcPath)) {
      fs.copyFileSync(srcPath, destPath);
      console.log(`已复制: ${file}`);
    }
  });

  // 复制 Playwright 浏览器（用于离线安装）
  console.log('正在复制 Playwright 浏览器...');
  const homeDir = require('os').homedir();
  const playwrightCachePath = path.join(homeDir, 'Library', 'Caches', 'ms-playwright');
  const playwrightDestPath = path.join(outputDir, 'playwright-browsers');

  if (fs.existsSync(playwrightCachePath)) {
    // 查找 chromium 目录
    const dirs = fs.readdirSync(playwrightCachePath);
    const chromiumDir = dirs.find(d => d.startsWith('chromium'));

    if (chromiumDir) {
      const chromiumSrc = path.join(playwrightCachePath, chromiumDir);
      const chromiumDest = path.join(playwrightDestPath, chromiumDir);

      // 确保目标目录存在
      fs.mkdirSync(playwrightDestPath, { recursive: true });

      // 使用系统 cp 命令复制（处理符号链接和特殊文件）
      try {
        execSync(`cp -R "${chromiumSrc}" "${playwrightDestPath}/"`, { stdio: 'inherit' });
        console.log(`已复制 Playwright Chromium: ${chromiumDir}`);
      } catch (copyError) {
        console.warn('警告: 复制 Playwright 浏览器时出错，尝试使用 ditto...');
        // 尝试使用 ditto（macOS 更可靠的复制工具）
        try {
          execSync(`ditto "${chromiumSrc}" "${chromiumDest}"`, { stdio: 'inherit' });
          console.log(`已使用 ditto 复制 Playwright Chromium: ${chromiumDir}`);
        } catch (dittoError) {
          console.warn('警告: 无法复制 Playwright 浏览器，应用将在首次启动时下载');
        }
      }
    } else {
      console.warn('警告: 未找到 Playwright Chromium，请先运行: uv run playwright install chromium');
    }
  } else {
    console.warn('警告: 未找到 Playwright 缓存目录，请先运行: uv run playwright install chromium');
  }

  console.log('后端构建完成！');
} catch (error) {
  console.error('后端构建失败:', error);
  process.exit(1);
}
