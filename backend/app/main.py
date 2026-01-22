from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源


app = FastAPI(
    title="Boss直聘自动化API",
    version="1.0.0",
    description="Boss直聘自动化工具后端API",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载前端静态文件(构建后)
# frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
# if frontend_dist.exists():
#     app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "Boss直聘自动化API运行正常"}


# 导入并注册路由
from app.routes import automation, candidates, templates, config, logs, greeting, accounts, notification, automation_templates

app.include_router(automation.router)
app.include_router(candidates.router)
app.include_router(templates.router)
app.include_router(automation_templates.router)
app.include_router(config.router)
app.include_router(logs.router)
app.include_router(greeting.router)
app.include_router(accounts.router)
app.include_router(notification.router)


if __name__ == "__main__":
    import uvicorn
    import os
    import sys

    # 从环境变量读取端口配置，默认使用27421
    port = int(os.getenv("API_PORT", os.getenv("PORT", 27421)))
    host = os.getenv("API_HOST", "0.0.0.0")

    # 检测是否在 PyInstaller 打包环境中运行
    is_frozen = getattr(sys, 'frozen', False)

    if is_frozen:
        # 打包环境：直接传递 app 对象，不使用 reload
        uvicorn.run(app, host=host, port=port, reload=False)
    else:
        # 开发环境：使用模块字符串支持热重载
        uvicorn.run("app.main:app", host=host, port=port, reload=True)
