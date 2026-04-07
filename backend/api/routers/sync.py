"""
股票同步路由

处理股票数据同步相关的API请求
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from backend.services.stock_sync import stock_sync_service
from backend.api.deps import get_current_active_user
from backend.database.models import User


router = APIRouter(
    prefix="/sync",
    tags=["sync"],
    responses={404: {"description": "Not found"}},
)


@router.post("/stock")
async def sync_stock_data(
    request: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    手动同步股票数据

    Args:
        request: 请求体，包含 source 字段（可选）
        current_user: 当前活跃用户

    Returns:
        dict: 同步结果
    """
    try:
        source = request.get("source", "auto")
        logger.info(f"用户 {current_user.username} 手动触发股票数据同步，数据源: {source}")
        success = stock_sync_service.sync_stock_data(source)
        if success:
            return {"status": "success", "message": "股票数据同步成功"}
        else:
            # 返回更详细的错误信息
            return {
                "status": "error",
                "message": "同步失败：所有数据源都无法访问，请稍后再试"
            }
    except Exception as e:
        logger.error(f"手动同步股票数据失败: {str(e)}")
        return {
            "status": "error",
            "message": f"同步失败：{str(e)}"
        }


@router.get("/stock/time")
async def get_sync_time(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取股票同步时间

    Args:
        current_user: 当前活跃用户

    Returns:
        dict: 同步时间
    """
    try:
        sync_time = stock_sync_service.get_sync_time()
        return {"status": "success", "data": {"sync_time": sync_time}}
    except Exception as e:
        logger.error(f"获取同步时间失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取同步时间失败")


@router.put("/stock/time")
async def set_sync_time(
    request: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    设置股票同步时间

    Args:
        request: 请求体，包含 sync_time 字段
        current_user: 当前活跃用户

    Returns:
        dict: 设置结果
    """
    try:
        sync_time = request.get("sync_time")
        if not sync_time:
            raise HTTPException(status_code=400, detail="缺少同步时间参数")
        
        # 验证时间格式
        from datetime import datetime
        datetime.strptime(sync_time, "%H:%M")
        
        success = stock_sync_service.save_sync_time(sync_time)
        if success:
            return {"status": "success", "message": "同步时间设置成功"}
        else:
            raise HTTPException(status_code=500, detail="同步时间设置失败")
    except ValueError:
        raise HTTPException(status_code=400, detail="时间格式错误，请使用 HH:MM 格式")
    except Exception as e:
        logger.error(f"设置同步时间失败: {str(e)}")
        raise HTTPException(status_code=500, detail="同步时间设置失败")
