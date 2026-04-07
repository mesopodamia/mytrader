"""
股票相关API路由

提供股票搜索、信息查询等功能
"""
from fastapi import APIRouter, Query


router = APIRouter(prefix="/stock", tags=["股票"])


@router.get("/search")
async def search_stocks(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回结果数量")
):
    """搜索股票"""
    # 只从本地数据库搜索
    from backend.services.stock_sync import stock_sync_service
    stocks = stock_sync_service.search_stocks(keyword, limit)
    if stocks:
        return {"status": "success", "data": stocks}
    else:
        return {"status": "success", "data": []}
