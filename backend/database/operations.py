"""
数据库操作

提供数据库CRUD操作
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.utils.config import settings
from backend.database.models import Base, User, UserRole, Portfolio, Position, Order, TradingLog, UserWatchlist, UserStockCategory, UserCategoryStock, StockAlert


# 创建数据库引擎
engine = create_engine(settings.data_db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    # 用户相关操作
    def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER
    ) -> User:
        """创建用户"""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_user(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        hashed_password: Optional[str] = None,
        is_active: Optional[bool] = None,
        role: Optional[UserRole] = None
    ) -> Optional[User]:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        if full_name is not None:
            user.full_name = full_name
        if email is not None:
            user.email = email
        if hashed_password is not None:
            user.hashed_password = hashed_password
        if is_active is not None:
            user.is_active = is_active
        if role is not None:
            user.role = role

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user_id: int):
        """更新最后登录时间"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()

    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    # 投资组合相关操作
    def create_portfolio(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        initial_capital: float = 1000000.0
    ) -> Portfolio:
        """创建投资组合"""
        portfolio = Portfolio(
            user_id=user_id,
            name=name,
            description=description,
            initial_capital=initial_capital,
            current_value=initial_capital
        )
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_portfolio_by_id(self, portfolio_id: int) -> Optional[Portfolio]:
        """通过ID获取投资组合"""
        return self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    def get_portfolios_by_user(self, user_id: int) -> List[Portfolio]:
        """获取用户的所有投资组合"""
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    def update_portfolio_value(self, portfolio_id: int, current_value: float):
        """更新投资组合价值"""
        portfolio = self.get_portfolio_by_id(portfolio_id)
        if portfolio:
            portfolio.current_value = current_value
            portfolio.total_return = current_value - portfolio.initial_capital
            portfolio.total_return_rate = (portfolio.total_return / portfolio.initial_capital) * 100
            portfolio.updated_at = datetime.utcnow()
            self.db.commit()

    # 持仓相关操作
    def create_or_update_position(
        self,
        portfolio_id: int,
        stock_code: str,
        stock_name: str,
        quantity: int,
        avg_cost: float,
        current_price: float
    ) -> Position:
        """创建或更新持仓"""
        position = self.db.query(Position).filter(
            Position.portfolio_id == portfolio_id,
            Position.stock_code == stock_code
        ).first()

        if position:
            position.quantity = quantity
            position.avg_cost = avg_cost
            position.current_price = current_price
            position.market_value = quantity * current_price
            position.profit_loss = (current_price - avg_cost) * quantity
            position.profit_loss_rate = ((current_price - avg_cost) / avg_cost) * 100 if avg_cost > 0 else 0
        else:
            position = Position(
                portfolio_id=portfolio_id,
                stock_code=stock_code,
                stock_name=stock_name,
                quantity=quantity,
                avg_cost=avg_cost,
                current_price=current_price,
                market_value=quantity * current_price,
                profit_loss=(current_price - avg_cost) * quantity,
                profit_loss_rate=((current_price - avg_cost) / avg_cost) * 100 if avg_cost > 0 else 0
            )
            self.db.add(position)

        self.db.commit()
        self.db.refresh(position)
        return position

    def get_positions_by_portfolio(self, portfolio_id: int) -> List[Position]:
        """获取投资组合的所有持仓"""
        return self.db.query(Position).filter(Position.portfolio_id == portfolio_id).all()

    # 订单相关操作
    def create_order(
        self,
        portfolio_id: int,
        stock_code: str,
        stock_name: str,
        action: str,
        order_type: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Order:
        """创建订单"""
        order = Order(
            portfolio_id=portfolio_id,
            stock_code=stock_code,
            stock_name=stock_name,
            action=action,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_orders_by_portfolio(self, portfolio_id: int) -> List[Order]:
        """获取投资组合的所有订单"""
        return self.db.query(Order).filter(Order.portfolio_id == portfolio_id).order_by(Order.created_at.desc()).all()

    def update_order_status(
        self,
        order_id: int,
        status: str,
        filled_quantity: Optional[int] = None,
        filled_price: Optional[float] = None
    ):
        """更新订单状态"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            if filled_quantity is not None:
                order.filled_quantity = filled_quantity
            if filled_price is not None:
                order.filled_price = filled_price
            order.updated_at = datetime.utcnow()
            self.db.commit()

    # 交易日志
    def create_trading_log(
        self,
        user_id: int,
        action: str,
        portfolio_id: Optional[int] = None,
        details: Optional[dict] = None
    ) -> TradingLog:
        """创建交易日志"""
        log = TradingLog(
            user_id=user_id,
            portfolio_id=portfolio_id,
            action=action,
            details=details or {}
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_trading_logs_by_user(self, user_id: int, limit: int = 100) -> List[TradingLog]:
        """获取用户的交易日志"""
        return self.db.query(TradingLog).filter(
            TradingLog.user_id == user_id
        ).order_by(TradingLog.created_at.desc()).limit(limit).all()

    # 自选股票相关操作
    def add_to_watchlist(self, user_id: int, stock_code: str, stock_name: str) -> UserWatchlist:
        """添加股票到自选列表"""
        # 检查是否已存在
        existing = self.db.query(UserWatchlist).filter(
            UserWatchlist.user_id == user_id,
            UserWatchlist.stock_code == stock_code
        ).first()
        
        if existing:
            return existing
        
        watchlist = UserWatchlist(
            user_id=user_id,
            stock_code=stock_code,
            stock_name=stock_name
        )
        self.db.add(watchlist)
        self.db.commit()
        self.db.refresh(watchlist)
        return watchlist

    def remove_from_watchlist(self, user_id: int, stock_code: str) -> bool:
        """从自选列表中移除股票"""
        watchlist = self.db.query(UserWatchlist).filter(
            UserWatchlist.user_id == user_id,
            UserWatchlist.stock_code == stock_code
        ).first()
        
        if not watchlist:
            return False
        
        self.db.delete(watchlist)
        self.db.commit()
        return True

    def get_user_watchlist(self, user_id: int) -> List[UserWatchlist]:
        """获取用户的自选股票列表"""
        return self.db.query(UserWatchlist).filter(
            UserWatchlist.user_id == user_id
        ).order_by(UserWatchlist.added_at.desc()).all()

    def is_in_watchlist(self, user_id: int, stock_code: str) -> bool:
        """检查股票是否在自选列表中"""
        watchlist = self.db.query(UserWatchlist).filter(
            UserWatchlist.user_id == user_id,
            UserWatchlist.stock_code == stock_code
        ).first()
        return watchlist is not None

    # 用户股票分类相关操作
    def create_stock_category(self, user_id: int, name: str, description: Optional[str] = None) -> UserStockCategory:
        """创建股票分类"""
        category = UserStockCategory(
            user_id=user_id,
            name=name,
            description=description
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_user_categories(self, user_id: int) -> List[UserStockCategory]:
        """获取用户的所有股票分类"""
        return self.db.query(UserStockCategory).filter(
            UserStockCategory.user_id == user_id
        ).order_by(UserStockCategory.created_at.desc()).all()

    def get_category_by_id(self, category_id: int, user_id: int) -> Optional[UserStockCategory]:
        """通过ID获取分类"""
        return self.db.query(UserStockCategory).filter(
            UserStockCategory.id == category_id,
            UserStockCategory.user_id == user_id
        ).first()

    def update_category(self, category_id: int, user_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[UserStockCategory]:
        """更新分类信息"""
        category = self.get_category_by_id(category_id, user_id)
        if not category:
            return None

        if name is not None:
            category.name = name
        if description is not None:
            category.description = description

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """删除分类"""
        category = self.get_category_by_id(category_id, user_id)
        if not category:
            return False

        # 先删除分类下的所有股票
        self.db.query(UserCategoryStock).filter(
            UserCategoryStock.category_id == category_id
        ).delete()

        # 再删除分类
        self.db.delete(category)
        self.db.commit()
        return True

    def add_stock_to_category(self, category_id: int, stock_code: str, stock_name: str) -> UserCategoryStock:
        """添加股票到分类"""
        # 检查是否已存在
        existing = self.db.query(UserCategoryStock).filter(
            UserCategoryStock.category_id == category_id,
            UserCategoryStock.stock_code == stock_code
        ).first()
        
        if existing:
            return existing
        
        category_stock = UserCategoryStock(
            category_id=category_id,
            stock_code=stock_code,
            stock_name=stock_name
        )
        self.db.add(category_stock)
        self.db.commit()
        self.db.refresh(category_stock)
        return category_stock

    def remove_stock_from_category(self, category_id: int, stock_code: str) -> bool:
        """从分类中移除股票"""
        category_stock = self.db.query(UserCategoryStock).filter(
            UserCategoryStock.category_id == category_id,
            UserCategoryStock.stock_code == stock_code
        ).first()
        
        if not category_stock:
            return False
        
        self.db.delete(category_stock)
        self.db.commit()
        return True

    def get_category_stocks(self, category_id: int) -> List[UserCategoryStock]:
        """获取分类中的所有股票"""
        return self.db.query(UserCategoryStock).filter(
            UserCategoryStock.category_id == category_id
        ).order_by(UserCategoryStock.added_at.desc()).all()

    def is_in_category(self, category_id: int, stock_code: str) -> bool:
        """检查股票是否在分类中"""
        category_stock = self.db.query(UserCategoryStock).filter(
            UserCategoryStock.category_id == category_id,
            UserCategoryStock.stock_code == stock_code
        ).first()
        return category_stock is not None

    # 股票预警相关操作
    def create_stock_alert(self, user_id: int, stock_code: str, stock_name: str, alert_type: str, condition: str, target_value: float) -> StockAlert:
        """创建股票预警"""
        alert = StockAlert(
            user_id=user_id,
            stock_code=stock_code,
            stock_name=stock_name,
            alert_type=alert_type,
            condition=condition,
            target_value=target_value
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_user_alerts(self, user_id: int) -> List[StockAlert]:
        """获取用户的所有预警"""
        return self.db.query(StockAlert).filter(
            StockAlert.user_id == user_id
        ).order_by(StockAlert.created_at.desc()).all()

    def get_alert_by_id(self, alert_id: int, user_id: int) -> Optional[StockAlert]:
        """通过ID获取预警"""
        return self.db.query(StockAlert).filter(
            StockAlert.id == alert_id,
            StockAlert.user_id == user_id
        ).first()

    def update_alert_status(self, alert_id: int, user_id: int, is_active: bool) -> Optional[StockAlert]:
        """更新预警状态"""
        alert = self.get_alert_by_id(alert_id, user_id)
        if not alert:
            return None

        alert.is_active = is_active
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def trigger_alert(self, alert_id: int) -> Optional[StockAlert]:
        """触发预警"""
        alert = self.db.query(StockAlert).filter(StockAlert.id == alert_id).first()
        if not alert:
            return None

        alert.triggered_at = datetime.utcnow()
        alert.is_active = False  # 触发后自动禁用
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def delete_alert(self, alert_id: int, user_id: int) -> bool:
        """删除预警"""
        alert = self.get_alert_by_id(alert_id, user_id)
        if not alert:
            return False

        self.db.delete(alert)
        self.db.commit()
        return True

    def get_active_alerts(self) -> List[StockAlert]:
        """获取所有激活的预警"""
        return self.db.query(StockAlert).filter(
            StockAlert.is_active == True
        ).all()
