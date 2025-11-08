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

  console.log('后端构建完成！');
} catch (error) {
  console.error('后端构建失败:', error);
  process.exit(1);
}
