"""
数据库模型

定义所有数据库表结构
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class UserRole(PyEnum):
    """用户角色"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # 关系
    portfolios = relationship("Portfolio", back_populates="user")
    trading_logs = relationship("TradingLog", back_populates="user")


class Portfolio(Base):
    """投资组合表"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    initial_capital = Column(Float, default=1000000.0)
    current_value = Column(Float, default=1000000.0)
    total_return = Column(Float, default=0.0)
    total_return_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio")
    orders = relationship("Order", back_populates="portfolio")


class Position(Base):
    """持仓表"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100))
    quantity = Column(Integer, default=0)
    avg_cost = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    market_value = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    profit_loss_rate = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    portfolio = relationship("Portfolio", back_populates="positions")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100))
    action = Column(String(10), nullable=False)  # buy/sell
    order_type = Column(String(20), default="market")  # market/limit
    quantity = Column(Integer, nullable=False)
    price = Column(Float)
    filled_quantity = Column(Integer, default=0)
    filled_price = Column(Float)
    status = Column(String(20), default="pending")  # pending/filled/cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    portfolio = relationship("Portfolio", back_populates="orders")


class TradingLog(Base):
    """交易日志表"""
    __tablename__ = "trading_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    action = Column(String(50), nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="trading_logs")


class SentimentAnalysis(Base):
    """舆情分析表"""
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(20), index=True)
    source = Column(String(50))  # news/social_media/forum
    sentiment = Column(String(20))  # positive/negative/neutral
    score = Column(Float)  # -1 to 1
    content = Column(Text)
    keywords = Column(JSON)
    analyzed_at = Column(DateTime, default=datetime.utcnow)


class UserWatchlist(Base):
    """用户自选股票表"""
    __tablename__ = "user_watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100))
    added_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", backref="watchlists")


class UserStockCategory(Base):
    """用户股票分类表"""
    __tablename__ = "user_stock_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", backref="categories")


class UserCategoryStock(Base):
    """用户分类股票关联表"""
    __tablename__ = "user_category_stocks"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("user_stock_categories.id"), nullable=False)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100))
    added_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    category = relationship("UserStockCategory", backref="stocks")


class StockAlert(Base):
    """股票预警表"""
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100))
    alert_type = Column(String(20), nullable=False)  # price, change, volume
    condition = Column(String(10), nullable=False)  # >, <, >=, <=
    target_value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User", backref="alerts")


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Stock(Base):
    """股票表"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    market = Column(String(50))
    industry = Column(String(100))
    sector = Column(String(100))
    price = Column(Float)
    change = Column(Float)
    change_rate = Column(Float)
    volume = Column(Integer)
    market_cap = Column(Float)
    pe = Column(Float)
    pb = Column(Float)
    eps = Column(Float)
    total_share = Column(Float)
    float_share = Column(Float)
    is_hs300 = Column(Boolean, default=False)
    is_zz500 = Column(Boolean, default=False)
    is_star = Column(Boolean, default=False)
    status = Column(String(20), default="active")  # active, delisted, suspended
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow)
