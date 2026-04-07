"""AI交易API路由"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel

from backend.core.engine import AITradingEngine
from backend.core.scheduler import TradingScheduler

router = APIRouter(prefix="/ai", tags=["AI交易"])

scheduler = TradingScheduler()


# Pydantic模型
class StockRequest(BaseModel):
    stock_codes: List[str]


class TradeRequest(BaseModel):
    stock_code: str
    action: str
    quantity: int


@router.get("/status")
async def get_status():
    """获取系统状态"""
    return {
        "status": "running",
        "scheduler": scheduler.get_status(),
        "timestamp": "2026-03-31"
    }


@router.post("/analyze")
async def analyze_stocks(request: StockRequest, background_tasks: BackgroundTasks):
    """分析股票"""
    try:
        result = await scheduler.run_once(request.stock_codes)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trade")
async def execute_trade(request: TradeRequest):
    """执行交易"""
    try:
        engine = AITradingEngine()
        decision = {
            "action": request.action,
            "confidence": 0.8,
            "position_ratio": 0.1
        }
        result = await engine.execute_trades({request.stock_code: decision})
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline")
async def run_pipeline(stock_codes: str):
    """运行完整交易流程"""
    try:
        codes = [code.strip() for code in stock_codes.split(",")]
        result = await scheduler.run_once(codes)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_scheduler():
    """启动调度器"""
    try:
        scheduler.start()
        return {"status": "success", "message": "调度器已启动"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_scheduler():
    """停止调度器"""
    try:
        scheduler.stop()
        return {"status": "success", "message": "调度器已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
