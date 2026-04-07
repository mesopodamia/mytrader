"""
雪球网API路由

提供雪球网模拟组合的REST API接口
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.adapters.xueqiu import XueqiuAdapter
from backend.utils.config import settings


router = APIRouter(prefix="/xueqiu", tags=["雪球网"])


# Pydantic模型
class OrderRequest(BaseModel):
    """下单请求"""
    portfolio_id: str
    stock_code: str
    action: str  # buy 或 sell
    quantity: int
    price: Optional[float] = None


class PortfolioCreateRequest(BaseModel):
    """创建组合请求"""
    name: str
    initial_capital: float = 1000000.0
    description: str = "AI自动交易组合"


class QuoteRequest(BaseModel):
    """行情请求"""
    stock_codes: List[str]


class HistoryRequest(BaseModel):
    """历史数据请求"""
    stock_code: str
    period: str = "1day"  # 1day, 1week, 1month
    count: int = 100


# 获取适配器实例
def get_adapter():
    """获取雪球网适配器实例"""
    return XueqiuAdapter(
        username=settings.xueqiu_username,
        password=settings.xueqiu_password
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "xueqiu"}


@router.post("/login")
async def login():
    """登录雪球网"""
    adapter = get_adapter()
    success = adapter.login()
    if success:
        return {"status": "success", "message": "登录成功"}
    else:
        raise HTTPException(status_code=401, detail="登录失败")


@router.post("/portfolio")
async def create_portfolio(request: PortfolioCreateRequest):
    """创建模拟组合"""
    adapter = get_adapter()
    if not adapter.login():
        raise HTTPException(status_code=401, detail="登录失败")

    portfolio = adapter.create_portfolio(
        name=request.name,
        initial_capital=request.initial_capital,
        description=request.description
    )

    if portfolio:
        return {"status": "success", "data": portfolio}
    else:
        raise HTTPException(status_code=400, detail="创建组合失败")


@router.get("/portfolio/{portfolio_id}")
async def get_portfolio_info(portfolio_id: str):
    """获取组合信息"""
    adapter = get_adapter()
    if not adapter.login():
        raise HTTPException(status_code=401, detail="登录失败")

    info = adapter.get_portfolio_info(portfolio_id)
    if info:
        return {"status": "success", "data": info}
    else:
        raise HTTPException(status_code=404, detail="组合不存在")


@router.get("/portfolio/{portfolio_id}/positions")
async def get_positions(portfolio_id: str):
    """获取持仓"""
    adapter = get_adapter()
    if not adapter.login():
        raise HTTPException(status_code=401, detail="登录失败")

    positions = adapter.get_positions(portfolio_id)
    if positions is not None:
        return {"status": "success", "data": positions}
    else:
        raise HTTPException(status_code=400, detail="获取持仓失败")


@router.post("/order")
async def place_order(request: OrderRequest):
    """下单"""
    adapter = get_adapter()
    if not adapter.login():
        raise HTTPException(status_code=401, detail="登录失败")

    order = adapter.place_order(
        portfolio_id=request.portfolio_id,
        stock_code=request.stock_code,
        action=request.action,
        quantity=request.quantity,
        price=request.price
    )

    if order:
        return {"status": "success", "data": order}
    else:
        raise HTTPException(status_code=400, detail="下单失败")


@router.post("/order/{portfolio_id}/{order_id}/cancel")
async def cancel_order(portfolio_id: str, order_id: str):
    """撤单"""
    adapter = get_adapter()
    if not adapter.login():
        raise HTTPException(status_code=401, detail="登录失败")

    success = adapter.cancel_order(portfolio_id, order_id)
    if success:
        return {"status": "success", "message": "撤单成功"}
    else:
        raise HTTPException(status_code=400, detail="撤单失败")


@router.get("/quotes")
async def get_realtime_quotes(
    stock_codes: str = Query(..., description="股票代码，逗号分隔"),
    source: str = Query("xueqiu", description="数据源: xueqiu, eastmoney")
):
    """获取实时行情"""
    codes = [code.strip() for code in stock_codes.split(",")]
    
    # 根据数据源选择适配器
    if source == "eastmoney":
        from backend.adapters.eastmoney import EastmoneyAdapter
        adapter = EastmoneyAdapter()
    else:
        adapter = get_adapter()

    quotes = adapter.get_realtime_quotes(codes)
    if quotes:
        return {"status": "success", "data": quotes}
    else:
        raise HTTPException(status_code=400, detail="获取行情失败")


@router.get("/history/{stock_code}")
async def get_historical_data(
    stock_code: str,
    period: str = Query("1day", description="周期: 1day, 1week, 1month"),
    count: int = Query(100, description="数据条数"),
    source: str = Query("xueqiu", description="数据源: xueqiu, eastmoney")
):
    """获取历史K线数据"""
    # 根据数据源选择适配器
    if source == "eastmoney":
        from backend.adapters.eastmoney import EastmoneyAdapter
        adapter = EastmoneyAdapter()
    else:
        adapter = get_adapter()

    history = adapter.get_historical_data(
        stock_code=stock_code,
        period=period,
        count=count
    )

    if history:
        return {"status": "success", "data": history}
    else:
        raise HTTPException(status_code=400, detail="获取历史数据失败")


@router.get("/stock/{stock_code}")
async def get_stock_info(
    stock_code: str,
    source: str = Query("xueqiu", description="数据源: xueqiu, eastmoney")
):
    """获取股票信息"""
    # 根据数据源选择适配器
    if source == "eastmoney":
        from backend.adapters.eastmoney import EastmoneyAdapter
        adapter = EastmoneyAdapter()
    else:
        adapter = get_adapter()

    info = adapter.get_stock_info(stock_code)
    if info:
        return {"status": "success", "data": info}
    else:
        raise HTTPException(status_code=404, detail="股票不存在")


@router.get("/search")
async def search_stocks(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回结果数量"),
    source: str = Query("local", description="数据源: local")
):
    """搜索股票"""
    # 只从本地数据库搜索
    from backend.services.stock_sync import stock_sync_service
    stocks = stock_sync_service.search_stocks(keyword, limit)
    if stocks:
        return {"status": "success", "data": stocks}
    else:
        return {"status": "success", "data": []}


@router.get("/industries")
async def get_industry_sectors(
    source: str = Query("xueqiu", description="数据源: xueqiu, eastmoney")
):
    """获取行业板块列表"""
    # 根据数据源选择适配器
    if source == "eastmoney":
        from backend.adapters.eastmoney import EastmoneyAdapter
        adapter = EastmoneyAdapter()
    else:
        adapter = get_adapter()

    sectors = adapter.get_industry_sectors()
    if sectors:
        return {"status": "success", "data": sectors}
    else:
        raise HTTPException(status_code=400, detail="获取行业板块失败")


@router.get("/industry/{industry_code}/stocks")
async def get_stocks_by_industry(
    industry_code: str,
    limit: int = Query(50, description="返回结果数量"),
    source: str = Query("xueqiu", description="数据源: xueqiu, eastmoney")
):
    """获取指定行业的股票列表"""
    # 根据数据源选择适配器
    if source == "eastmoney":
        from backend.adapters.eastmoney import EastmoneyAdapter
        adapter = EastmoneyAdapter()
    else:
        adapter = get_adapter()

    stocks = adapter.get_stocks_by_industry(industry_code, limit)
    if stocks:
        return {"status": "success", "data": stocks}
    else:
        raise HTTPException(status_code=400, detail="获取行业股票失败")
