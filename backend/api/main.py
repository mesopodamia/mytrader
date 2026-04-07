"""FastAPI 主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import WebSocket
from loguru import logger
from pathlib import Path

# 导入路由
from backend.api.routers import xueqiu, auth, watchlist, category, alert, sync, stock
from backend.database import init_db

# 前端目录
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"

# 创建FastAPI应用
app = FastAPI(
    title="AI Trader API",
    description="AI驱动的模拟炒股系统",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(xueqiu.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
app.include_router(category.router, prefix="/api/v1")
app.include_router(alert.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")


# WebSocket 连接管理
active_connections = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            # 处理消息
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # 移除连接
        active_connections.remove(websocket)
        await websocket.close()


@app.get("/api")
async def root():
    """API根路径"""
    return {
        "message": "AI Trader API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 前端静态文件服务
if FRONTEND_DIR.exists():
    # 挂载assets目录
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        """服务首页"""
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)
        return HTMLResponse(content="<h1>AI Trader</h1><p>Frontend not built yet.</p>")

    @app.get("/{path:path}", response_class=HTMLResponse)
    async def serve_spa(path: str):
        """服务SPA路由 - 所有非API路径都返回index.html"""
        # 排除API路径
        if path.startswith("api/") or path.startswith("docs") or path.startswith("openapi.json"):
            return HTMLResponse(content="Not Found", status_code=404)

        # 返回index.html让前端路由处理
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)
        return HTMLResponse(content="<h1>AI Trader</h1><p>Frontend not built yet.</p>")
else:
    @app.get("/")
    async def no_frontend():
        return {
            "message": "AI Trader API",
            "warning": "Frontend not built yet. Please run 'cd frontend && npm run build'",
            "docs": "/docs"
        }


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("=" * 50)
    logger.info("AI Trader API 启动中...")
    logger.info(f"前端目录: {FRONTEND_DIR}")
    logger.info(f"前端目录存在: {FRONTEND_DIR.exists()}")
    if FRONTEND_DIR.exists():
        logger.info(f"index.html存在: {(FRONTEND_DIR / 'index.html').exists()}")
    # 初始化数据库
    init_db()
    logger.info("数据库初始化完成")
    # 初始化默认数据
    from backend.database.init_defaults import init_defaults
    init_defaults()
    logger.info("默认数据初始化完成")
    # 启动股票同步服务
    from backend.services.stock_sync import start_stock_sync
    await start_stock_sync()
    logger.info("股票同步服务已启动")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("AI Trader API 关闭中...")
