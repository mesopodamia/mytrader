"""
股票预警API路由

提供股票预警的REST API接口
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.operations import get_db, DatabaseManager
from backend.api.deps import get_current_user
from backend.database.models import User


router = APIRouter(prefix="/alert", tags=["股票预警"])


# Pydantic模型
class AlertCreate(BaseModel):
    """创建预警请求"""
    stock_code: str
    stock_name: str
    alert_type: str  # price, change, volume
    condition: str  # >, <, >=, <=
    target_value: float


class AlertUpdate(BaseModel):
    """更新预警请求"""
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    """预警响应"""
    id: int
    stock_code: str
    stock_name: str
    alert_type: str
    condition: str
    target_value: float
    is_active: bool
    created_at: str
    triggered_at: Optional[str]

    class Config:
        from_attributes = True


@router.get("/")
async def get_user_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有预警"""
    db_manager = DatabaseManager()
    alerts = db_manager.get_user_alerts(current_user.id)
    return alerts


@router.post("/")
async def create_alert(
    request: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新预警"""
    db_manager = DatabaseManager()
    alert = db_manager.create_stock_alert(
        user_id=current_user.id,
        stock_code=request.stock_code,
        stock_name=request.stock_name,
        alert_type=request.alert_type,
        condition=request.condition,
        target_value=request.target_value
    )
    return alert


@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取预警详情"""
    db_manager = DatabaseManager()
    alert = db_manager.get_alert_by_id(alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    return alert


@router.put("/{alert_id}")
async def update_alert(
    alert_id: int,
    request: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新预警状态"""
    db_manager = DatabaseManager()
    if request.is_active is not None:
        alert = db_manager.update_alert_status(alert_id, current_user.id, request.is_active)
        if not alert:
            raise HTTPException(status_code=404, detail="预警不存在")
        return alert
    else:
        raise HTTPException(status_code=400, detail="请提供要更新的字段")


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除预警"""
    db_manager = DatabaseManager()
    success = db_manager.delete_alert(alert_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="预警不存在")
    return {"status": "success", "message": "预警删除成功"}
