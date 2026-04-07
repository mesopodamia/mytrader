"""
重置管理员密码

将管理员用户的密码重置为默认密码
"""
from loguru import logger
from backend.database.operations import DatabaseManager
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password):
    """获取密码哈希"""
    return pwd_context.hash(password)

def reset_admin_password():
    """
    重置管理员密码
    """
    db = DatabaseManager()
    
    # 查找管理员用户
    admin_user = db.get_user_by_username("admin")
    if not admin_user:
        logger.error("管理员用户不存在")
        return
    
    # 生成正确的 pbkdf2_sha256 哈希密码
    hashed_password = get_password_hash("admin123")
    updated_user = db.update_user(
        admin_user.id,
        hashed_password=hashed_password
    )
    
    if updated_user:
        logger.info("管理员密码重置成功")
        logger.info(f"用户名: {updated_user.username}")
        logger.info(f"密码: admin123")
    else:
        logger.error("管理员密码重置失败")


if __name__ == "__main__":
    reset_admin_password()
