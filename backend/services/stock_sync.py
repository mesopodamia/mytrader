"""
股票数据同步服务

用于定时从外网同步股票数据到本地数据库
"""
import asyncio
import schedule
import time
from loguru import logger
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.database.operations import get_db
from backend.database.models import Stock, SystemConfig
from backend.adapters.akshare import AKShareAdapter
from backend.adapters.baostock import BaostockAdapter
from backend.adapters.biying import BiyingAdapter


import threading


class StockSyncService:
    """股票数据同步服务"""

    def __init__(self):
        self.akshare_adapter = AKShareAdapter()
        self.baostock_adapter = BaostockAdapter()
        self.biying_adapter = BiyingAdapter()
        self.db: Session = None
        self.sync_time = "01:00"  # 默认同步时间
        self.sync_lock = threading.Lock()  # 同步锁，确保同一时间只有一个同步操作在进行

    def init_db(self):
        """初始化数据库连接"""
        if not self.db:
            self.db = next(get_db())
            # 加载同步时间配置
            self.load_sync_time()

    def load_sync_time(self):
        """加载同步时间配置"""
        try:
            config = self.db.query(SystemConfig).filter(SystemConfig.key == "stock_sync_time").first()
            if config:
                self.sync_time = config.value
                logger.info(f"加载股票同步时间: {self.sync_time}")
        except Exception as e:
            logger.error(f"加载同步时间失败: {str(e)}")

    def save_sync_time(self, sync_time: str):
        """保存同步时间配置"""
        try:
            self.init_db()
            config = self.db.query(SystemConfig).filter(SystemConfig.key == "stock_sync_time").first()
            if config:
                config.value = sync_time
                config.updated_at = datetime.utcnow()
            else:
                config = SystemConfig(
                    key="stock_sync_time",
                    value=sync_time,
                    description="股票数据自动同步时间"
                )
                self.db.add(config)
            self.db.commit()
            self.sync_time = sync_time
            # 重新设置定时任务
            self._update_schedule()
            logger.info(f"保存股票同步时间: {sync_time}")
            return True
        except Exception as e:
            logger.error(f"保存同步时间失败: {str(e)}")
            self.db.rollback()
            return False

    def get_sync_time(self):
        """获取同步时间配置"""
        self.init_db()
        return self.sync_time

    def sync_stock_data(self, source: str = "auto"):
        """同步股票数据

        Args:
            source: 数据源，可选值：auto, xueqiu, eastmoney, sina
        """
        # 检查是否已经有同步操作在进行
        if not self.sync_lock.acquire(blocking=False):
            logger.warning("同步操作正在进行中，请勿重复触发")
            return False

        try:
            logger.info(f"开始同步股票数据，数据源: {source}...")
            self.init_db()

            # 尝试从指定数据源获取数据
            total_sync = 0
            
            # 根据选择的数据源进行同步
            if source == "auto":
                # 自动尝试所有数据源，优先使用 AKShare、Baostock 和 Biying
                sources = ["akshare", "baostock", "biying"]
                for src in sources:
                    if total_sync > 0:
                        break
                    try:
                        logger.info(f"尝试从 {src} 获取数据...")
                        total_sync += self._sync_from_source(src)
                        logger.info(f"从 {src} 获取数据成功，同步了 {total_sync} 只股票")
                    except Exception as e:
                        logger.warning(f"从{src}获取数据失败: {str(e)}")
            else:
                # 使用指定的数据源
                logger.info(f"使用指定的数据源 {source} 进行同步...")
                total_sync = self._sync_from_source(source)
                logger.info(f"从 {source} 获取数据成功，同步了 {total_sync} 只股票")

            if total_sync > 0:
                logger.info(f"股票数据同步完成，共同步 {total_sync} 只股票")
                return True
            else:
                logger.warning("所有数据源都获取失败，未同步任何股票数据")
                return False
        except Exception as e:
            logger.error(f"同步股票数据失败: {str(e)}")
            return False
        finally:
            # 释放锁
            self.sync_lock.release()

    def _sync_from_source(self, source: str) -> int:
        """从指定数据源同步股票数据

        Args:
            source: 数据源

        Returns:
            int: 同步的股票数量
        """
        total_sync = 0
        
        # 内置的股票列表，当所有外部数据源都失败时使用
        built_in_stocks = [
            {"code": "600000", "name": "浦发银行", "market": "沪市"},
            {"code": "600519", "name": "贵州茅台", "market": "沪市"},
            {"code": "000001", "name": "平安银行", "market": "深市"},
            {"code": "000858", "name": "五粮液", "market": "深市"},
            {"code": "002594", "name": "比亚迪", "market": "深市"},
            {"code": "601318", "name": "中国平安", "market": "沪市"},
            {"code": "600036", "name": "招商银行", "market": "沪市"},
            {"code": "601888", "name": "中国中免", "market": "沪市"},
            {"code": "601899", "name": "紫金矿业", "market": "沪市"},
            {"code": "000333", "name": "美的集团", "market": "深市"}
        ]
        
        # 如果是内置数据源，直接使用内置股票列表
        if source == "built_in":
            logger.info("使用内置股票列表进行同步")
            for stock in built_in_stocks:
                self._save_stock(stock, "内置股票")
                total_sync += 1
            return total_sync
        
        # 从外部数据源获取股票
        sectors = []
        
        # 获取行业板块列表
        if source == "akshare":
            sectors = self.akshare_adapter.get_industry_sectors()
        elif source == "baostock":
            sectors = self.baostock_adapter.get_industry_sectors()
        elif source == "biying":
            sectors = self.biying_adapter.get_industry_sectors()
        
        if not sectors:
            logger.warning(f"从{source}获取行业板块失败，使用默认板块")
            sectors = [
                {"code": "100", "name": "沪深300"},
                {"code": "101", "name": "中证500"},
                {"code": "102", "name": "创业板"}
            ]

        # 遍历每个板块，同步股票数据
        if source == "biying":
            # 必盈API 没有直接提供行业股票列表接口，返回的是所有股票
            # 只需要调用一次 get_stocks_by_industry 方法获取所有股票
            logger.info(f"从{source}同步所有股票")
            stocks = self.biying_adapter.get_stocks_by_industry(sectors[0]['code'])
            if stocks:
                for stock in stocks:
                    self._save_stock(stock, "必盈API")
                    total_sync += 1
        else:
            # 其他数据源按照板块同步
            for sector in sectors:
                logger.info(f"从{source}同步板块: {sector['name']} ({sector['code']})")
                stocks = []
                
                if source == "akshare":
                    stocks = self.akshare_adapter.get_stocks_by_industry(sector['code'], limit=100)
                elif source == "baostock":
                    stocks = self.baostock_adapter.get_stocks_by_industry(sector['code'], limit=100)
                
                if stocks:
                    for stock in stocks:
                        self._save_stock(stock, sector['name'])
                        total_sync += 1
        
        # 如果外部数据源失败，使用内置股票列表
        if total_sync == 0:
            logger.warning(f"从{source}获取股票失败，使用内置股票列表")
            for stock in built_in_stocks:
                self._save_stock(stock, "内置股票")
                total_sync += 1
        
        return total_sync

    def _save_stock(self, stock_data: dict, industry: str):
        """保存股票数据到数据库"""
        try:
            # 查找现有股票
            stock = self.db.query(Stock).filter(Stock.code == stock_data['code']).first()

            if stock:
                # 更新现有股票
                stock.name = stock_data.get('name', stock.name)
                stock.market = stock_data.get('market', stock.market)
                stock.industry = industry
                stock.sector = stock_data.get('sector', stock.sector)
                stock.price = stock_data.get('current', stock.price)
                stock.change = stock_data.get('change', stock.change)
                stock.change_rate = stock_data.get('change_percent', stock.change_rate)
                stock.volume = stock_data.get('volume', stock.volume)
                stock.market_cap = stock_data.get('market_cap', stock.market_cap)
                stock.pe = stock_data.get('pe_ttm', stock.pe)
                stock.pb = stock_data.get('pb', stock.pb)
                stock.eps = stock_data.get('eps', stock.eps)
                stock.synced_at = datetime.utcnow()
            else:
                # 创建新股票
                stock = Stock(
                    code=stock_data['code'],
                    name=stock_data.get('name', ''),
                    market=stock_data.get('market', ''),
                    industry=industry,
                    sector=stock_data.get('sector', ''),
                    price=stock_data.get('current', 0.0),
                    change=stock_data.get('change', 0.0),
                    change_rate=stock_data.get('change_percent', 0.0),
                    volume=stock_data.get('volume', 0),
                    market_cap=stock_data.get('market_cap', 0.0),
                    pe=stock_data.get('pe_ttm', 0.0),
                    pb=stock_data.get('pb', 0.0),
                    eps=stock_data.get('eps', 0.0),
                    synced_at=datetime.utcnow()
                )
                self.db.add(stock)

            self.db.commit()
        except Exception as e:
            logger.error(f"保存股票数据失败: {str(e)}")
            self.db.rollback()

    def search_stocks(self, keyword: str, limit: int = 10) -> list:
        """从本地数据库搜索股票"""
        self.init_db()
        
        try:
            # 搜索股票代码或名称
            stocks = self.db.query(Stock).filter(
                (Stock.code.ilike(f"%{keyword}%") | Stock.name.ilike(f"%{keyword}%") )
                & (Stock.status == "active")
            ).limit(limit).all()

            # 转换为前端需要的格式
            result = []
            for stock in stocks:
                result.append({
                    "code": stock.code,
                    "name": stock.name,
                    "market": stock.market,
                    "industry": stock.industry,
                    "price": stock.price,
                    "change_rate": stock.change_rate
                })

            # 如果没有结果，返回一些默认股票
            if not result:
                # 从内置股票列表中选择一些相关的股票
                built_in_stocks = [
                    {"code": "600000", "name": "浦发银行", "market": "沪市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0},
                    {"code": "600519", "name": "贵州茅台", "market": "沪市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0},
                    {"code": "000001", "name": "平安银行", "market": "深市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0},
                    {"code": "000858", "name": "五粮液", "market": "深市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0},
                    {"code": "002594", "name": "比亚迪", "market": "深市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0}
                ]
                result = built_in_stocks[:limit]

            return result
        except Exception as e:
            logger.error(f"搜索股票失败: {str(e)}")
            # 发生错误时返回默认股票
            return [
                {"code": "600000", "name": "浦发银行", "market": "沪市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0},
                {"code": "600519", "name": "贵州茅台", "market": "沪市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0},
                {"code": "000001", "name": "平安银行", "market": "深市", "industry": "内置股票", "price": 0.0, "change_rate": 0.0}
            ]

    def _update_schedule(self):
        """更新定时任务"""
        # 清除所有现有任务
        schedule.clear()
        # 添加新的定时任务
        schedule.every().day.at(self.sync_time).do(self.sync_stock_data)
        logger.info(f"更新股票同步定时任务: 每天 {self.sync_time}")

    def start_schedule(self):
        """启动定时任务"""
        # 加载同步时间
        self.init_db()
        # 设置定时任务
        self._update_schedule()
        
        # 启动时先同步一次
        self.sync_stock_data()
        
        logger.info("股票数据同步定时任务已启动")
        
        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(60)


# 全局实例
stock_sync_service = StockSyncService()


async def start_stock_sync():
    """启动股票同步服务"""
    # 在后台线程中运行定时任务
    import threading
    sync_thread = threading.Thread(target=stock_sync_service.start_schedule, daemon=True)
    sync_thread.start()
    logger.info("股票同步服务已启动")
