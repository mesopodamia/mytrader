"""
初始化默认数据

创建默认管理员用户和其他必要的默认数据
"""
from loguru import logger
from backend.database.operations import DatabaseManager
from backend.database.models import UserRole
from backend.api.routers.auth import get_password_hash


def init_default_admin():
    """
    初始化默认管理员用户
    """
    db = DatabaseManager()
    
    # 检查是否已存在管理员用户
    admin_user = db.get_user_by_username("admin")
    if admin_user:
        logger.info("默认管理员用户已存在")
        return
    
    # 创建默认管理员用户
    hashed_password = get_password_hash("admin123")  # 默认密码
    admin_user = db.create_user(
        username="admin",
        email="admin@example.com",
        hashed_password=hashed_password,
        full_name="系统管理员",
        role=UserRole.ADMIN
    )
    
    logger.info(f"默认管理员用户创建成功: {admin_user.username}")


def init_defaults():
    """
    初始化所有默认数据
    """
    logger.info("开始初始化默认数据...")
    init_default_admin()
    logger.info("默认数据初始化完成")


if __name__ == "__main__":
    init_defaults()
