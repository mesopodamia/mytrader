"""AI Trader Configuration"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = Field(default="AI Trader", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    # 数据库配置
    data_db_url: str = Field(default="sqlite:///./ai_trader.db", alias="DATA_DB_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # 雪球网配置
    xueqiu_username: Optional[str] = Field(default=None, alias="XUEQIU_USERNAME")
    xueqiu_password: Optional[str] = Field(default=None, alias="XUEQIU_PASSWORD")

    # OpenClaw配置
    openclaw_api_key: Optional[str] = Field(default=None, alias="OPENCLAW_API_KEY")
    openclaw_api_url: str = Field(default="https://api.openclaw.ai", alias="OPENCLAW_API_URL")

    # API服务配置
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_reload: bool = Field(default=True, alias="API_RELOAD")

    # JWT认证配置
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60 * 24, alias="ACCESS_TOKEN_EXPIRE_MINUTES")  # 24小时

    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/ai_trader.log", alias="LOG_FILE")

    # 交易配置
    initial_capital: float = Field(default=1000000.0, alias="INITIAL_CAPITAL")
    max_position_ratio: float = Field(default=0.2, alias="MAX_POSITION_RATIO")
    daily_loss_limit: float = Field(default=0.02, alias="DAILY_LOSS_LIMIT")
    trading_frequency_limit: int = Field(default=10, alias="TRADING_FREQUENCY_LIMIT")

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
