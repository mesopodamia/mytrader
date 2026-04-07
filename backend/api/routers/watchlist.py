"""
自选股票路由

提供用户自选股票的管理功能
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from backend.database.models import User, UserWatchlist
from backend.database.operations import DatabaseManager
from backend.api.routers.auth import get_current_active_user


router = APIRouter(prefix="/watchlist", tags=["自选股票"])


# Pydantic模型
class StockItem(BaseModel):
    """股票项目"""
    stock_code: str = Field(..., min_length=1, max_length=20)
    stock_name: str = Field(..., min_length=1, max_length=100)


class WatchlistResponse(BaseModel):
    """自选股票响应"""
    id: int
    stock_code: str
    stock_name: str
    added_at: str

    class Config:
        from_attributes = True


class WatchlistAction(BaseModel):
    """自选股票操作"""
    stock_code: str
    stock_name: str


# 路由
@router.get("", response_model=List[WatchlistResponse])
async def get_watchlist(current_user: User = Depends(get_current_active_user)):
    """
    获取用户的自选股票列表
    """
    db = DatabaseManager()
    watchlist = db.get_user_watchlist(current_user.id)
    return watchlist


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    stock: WatchlistAction,
    current_user: User = Depends(get_current_active_user)
):
    """
    添加股票到自选列表
    """
    db = DatabaseManager()
    watchlist_item = db.add_to_watchlist(
        user_id=current_user.id,
        stock_code=stock.stock_code,
        stock_name=stock.stock_name
    )
    return watchlist_item


@router.delete("/{stock_code}")
async def remove_from_watchlist(
    stock_code: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    从自选列表中移除股票
    """
    db = DatabaseManager()
    success = db.remove_from_watchlist(current_user.id, stock_code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="股票不在自选列表中"
        )
    return {"message": "股票已从自选列表中移除"}


@router.get("/check/{stock_code}")
async def check_watchlist(
    stock_code: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    检查股票是否在自选列表中
    """
    db = DatabaseManager()
    is_in = db.is_in_watchlist(current_user.id, stock_code)
    return {"is_in_watchlist": is_in}
