"""
用户股票分类API路由

提供用户自定义股票分类的REST API接口
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.operations import get_db, DatabaseManager
from backend.api.deps import get_current_user
from backend.database.models import User


router = APIRouter(prefix="/category", tags=["股票分类"])


# Pydantic模型
class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryStockAdd(BaseModel):
    """添加股票到分类请求"""
    stock_code: str
    stock_name: str


class CategoryResponse(BaseModel):
    """分类响应"""
    id: int
    name: str
    description: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class CategoryStockResponse(BaseModel):
    """分类股票响应"""
    id: int
    stock_code: str
    stock_name: str
    added_at: str

    class Config:
        from_attributes = True


@router.get("/")
async def get_user_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有分类"""
    db_manager = DatabaseManager()
    categories = db_manager.get_user_categories(current_user.id)
    return categories


@router.post("/")
async def create_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新分类"""
    db_manager = DatabaseManager()
    category = db_manager.create_stock_category(
        user_id=current_user.id,
        name=request.name,
        description=request.description
    )
    return category


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类详情"""
    db_manager = DatabaseManager()
    category = db_manager.get_category_by_id(category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新分类信息"""
    db_manager = DatabaseManager()
    category = db_manager.update_category(
        category_id=category_id,
        user_id=current_user.id,
        name=request.name,
        description=request.description
    )
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除分类"""
    db_manager = DatabaseManager()
    success = db_manager.delete_category(category_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"status": "success", "message": "分类删除成功"}


@router.get("/{category_id}/stocks")
async def get_category_stocks(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类中的股票"""
    db_manager = DatabaseManager()
    # 先检查分类是否存在且属于当前用户
    category = db_manager.get_category_by_id(category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 获取分类中的股票
    stocks = db_manager.get_category_stocks(category_id)
    return stocks


@router.post("/{category_id}/stocks")
async def add_stock_to_category(
    category_id: int,
    request: CategoryStockAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加股票到分类"""
    db_manager = DatabaseManager()
    # 先检查分类是否存在且属于当前用户
    category = db_manager.get_category_by_id(category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 添加股票到分类
    stock = db_manager.add_stock_to_category(
        category_id=category_id,
        stock_code=request.stock_code,
        stock_name=request.stock_name
    )
    return stock


@router.delete("/{category_id}/stocks/{stock_code}")
async def remove_stock_from_category(
    category_id: int,
    stock_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从分类中移除股票"""
    db_manager = DatabaseManager()
    # 先检查分类是否存在且属于当前用户
    category = db_manager.get_category_by_id(category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 从分类中移除股票
    success = db_manager.remove_stock_from_category(category_id, stock_code)
    if not success:
        raise HTTPException(status_code=404, detail="股票不在分类中")
    return {"status": "success", "message": "股票移除成功"}
