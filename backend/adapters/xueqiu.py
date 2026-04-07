"""
雪球网适配器 - 模拟组合交易接口

主要功能：
1. 账户管理（创建模拟组合、获取组合信息）
2. 交易执行（买卖下单、撤单）
3. 数据获取（实时行情、历史数据）
4. 持仓管理（查询持仓、资产分析）
"""

import asyncio
import time
from typing import Optional, Dict, List, Any
from loguru import logger
import aiohttp
import requests
from datetime import datetime, timedelta


class XueqiuAdapter:
    """雪球网模拟组合适配器"""

    def __init__(self, username: str = None, password: str = None):
        """
        初始化雪球网适配器

        Args:
            username: 雪球用户名（可选）
            password: 雪球密码（可选）
        """
        self.username = username
        self.password = password
        self.base_url = "https://xueqiu.com"
        self.session = requests.Session()
        self.cookies = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://xueqiu.com/",
        }

    def login(self) -> bool:
        """
        登录雪球网

        Returns:
            bool: 登录是否成功
        """
        try:
            # 首次访问主页获取Cookie
            response = self.session.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                self.cookies = response.cookies.get_dict()
                logger.info("访问雪球网主页成功")

            # 模拟登录流程（注意：雪球网可能有反爬虫机制）
            login_url = f"{self.base_url}/user/login"
            login_data = {
                "username": self.username,
                "password": self.password,
                "remember_me": "true"
            }

            response = self.session.post(
                login_url,
                data=login_data,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    logger.info(f"登录成功: {self.username}")
                    return True
                else:
                    logger.error(f"登录失败: {result.get('error_description')}")
                    return False

        except Exception as e:
            logger.error(f"登录过程出错: {str(e)}")
            return False

    def create_portfolio(
        self,
        name: str,
        initial_capital: float = 1000000.0,
        description: str = "AI自动交易组合"
    ) -> Optional[Dict[str, Any]]:
        """
        创建新的模拟组合

        Args:
            name: 组合名称
            initial_capital: 初始资金
            description: 组合描述

        Returns:
            Dict: 组合信息，失败返回None
        """
        try:
            url = f"{self.base_url}/portfolios/new"
            data = {
                "name": name,
                "description": description,
                "initial_capital": initial_capital,
                "type": "stock"  # 股票类型
            }

            response = self.session.post(
                url,
                json=data,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    portfolio_id = result.get("data", {}).get("id")
                    logger.info(f"创建组合成功: {name} (ID: {portfolio_id})")
                    return result.get("data")
                else:
                    logger.error(f"创建组合失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"创建组合失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"创建组合出错: {str(e)}")
            return None

    def get_portfolio_info(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """
        获取组合详情

        Args:
            portfolio_id: 组合ID

        Returns:
            Dict: 组合信息，失败返回None
        """
        try:
            url = f"{self.base_url}/portfolios/{portfolio_id}"
            response = self.session.get(
                url,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    return result.get("data")
                else:
                    logger.error(f"获取组合信息失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"获取组合信息失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取组合信息出错: {str(e)}")
            return None

    def get_positions(self, portfolio_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取持仓

        Args:
            portfolio_id: 组合ID

        Returns:
            List[Dict]: 持仓列表，失败返回None
        """
        try:
            url = f"{self.base_url}/portfolios/{portfolio_id}/positions"
            response = self.session.get(
                url,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    positions = result.get("data", {}).get("list", [])
                    logger.info(f"获取持仓成功: {len(positions)} 只股票")
                    return positions
                else:
                    logger.error(f"获取持仓失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"获取持仓失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取持仓出错: {str(e)}")
            return None

    def place_order(
        self,
        portfolio_id: str,
        stock_code: str,
        action: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        下单

        Args:
            portfolio_id: 组合ID
            stock_code: 股票代码（如：SH000001）
            action: 交易动作 'buy' 或 'sell'
            quantity: 数量
            price: 价格，None表示市价单

        Returns:
            Dict: 订单信息，失败返回None
        """
        try:
            url = f"{self.base_url}/portfolios/{portfolio_id}/orders"
            data = {
                "stock_code": stock_code,
                "action": action,
                "quantity": quantity,
                "order_type": "market" if price is None else "limit",
                "price": price
            }

            response = self.session.post(
                url,
                json=data,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    order_id = result.get("data", {}).get("id")
                    logger.info(
                        f"下单成功: {action} {quantity}股 {stock_code} "
                        f"@{price if price else '市价'} (订单ID: {order_id})"
                    )
                    return result.get("data")
                else:
                    logger.error(f"下单失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"下单失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"下单出错: {str(e)}")
            return None

    def cancel_order(self, portfolio_id: str, order_id: str) -> bool:
        """
        撤单

        Args:
            portfolio_id: 组合ID
            order_id: 订单ID

        Returns:
            bool: 是否成功
        """
        try:
            url = f"{self.base_url}/portfolios/{portfolio_id}/orders/{order_id}/cancel"
            response = self.session.post(
                url,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    logger.info(f"撤单成功: {order_id}")
                    return True
                else:
                    logger.error(f"撤单失败: {result.get('error_description')}")
                    return False
            else:
                logger.error(f"撤单失败: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"撤单出错: {str(e)}")
            return False

    def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict: 行情数据，失败返回None
        """
        try:
            # 雪球网实时行情API
            symbols = ",".join([f"SH{code}" if code.startswith("6") else f"SZ{code}"
                               for code in stock_codes])
            url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json"
            params = {
                "symbol": symbols,
                "extend": "detail"
            }

            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    data = result.get("data", {})
                    logger.info(f"获取实时行情成功: {len(data)} 只股票")
                    return data
                else:
                    logger.error(f"获取实时行情失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"获取实时行情失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取实时行情出错: {str(e)}")
            return None

    def get_historical_data(
        self,
        stock_code: str,
        period: str = "1day",
        count: int = 100,
        include_current: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        获取历史K线数据

        Args:
            stock_code: 股票代码
            period: 周期（1day, 1week, 1month）
            count: 数据条数
            include_current: 是否包含当天数据

        Returns:
            List[Dict]: K线数据列表，失败返回None
        """
        try:
            symbol = f"SH{stock_code}" if stock_code.startswith("6") else f"SZ{stock_code}"
            url = f"https://stock.xueqiu.com/v5/stock/kline.json"
            params = {
                "symbol": symbol,
                "begin": int(time.time() * 1000 - 365 * 24 * 60 * 60 * 1000),  # 一年前
                "period": period,
                "type": "before,after",
                "count": count,
                "indicator": "kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
            }

            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    data = result.get("data", {}).get("item", [])
                    logger.info(f"获取历史数据成功: {symbol} ({len(data)}条)")
                    return data
                else:
                    logger.error(f"获取历史数据失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"获取历史数据失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取历史数据出错: {str(e)}")
            return None

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息

        Args:
            stock_code: 股票代码

        Trader:
            Dict: 股票信息，失败返回None
        """
        try:
            symbol = f"SH{stock_code}" if stock_code.startswith("6") else f"SZ{stock_code}"
            url = f"https://stock.xueqiu.com/v5/stock/fundamental.json"
            params = {
                "symbol": symbol,
                "type": "all"
            }

            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    data = result.get("data", {})
                    logger.info(f"获取股票信息成功: {symbol}")
                    return data
                else:
                    logger.error(f"获取股票信息失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"获取股票信息失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取股票信息出错: {str(e)}")
            return None

    def search_stocks(self, keyword: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        搜索股票

        Args:
            keyword: 搜索关键词（股票代码或名称）
            limit: 返回结果数量

        Returns:
            List[Dict]: 股票列表，失败返回None
        """
        try:
            url = f"https://xueqiu.com/stock/search.json"
            params = {
                "code": keyword,
                "size": limit
            }

            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    stocks = result.get("data", {}).get("stocks", [])
                    logger.info(f"搜索股票成功: {keyword} ({len(stocks)}条结果)")
                    return stocks
                else:
                    logger.error(f"搜索股票失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"搜索股票失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"搜索股票出错: {str(e)}")
            return None

    def get_industry_sectors(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取行业板块列表

        Returns:
            List[Dict]: 行业板块列表，失败返回None
        """
        try:
            url = f"https://xueqiu.com/hq/industry/list.json"
            
            response = self.session.get(
                url,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    sectors = result.get("data", {}).get("list", [])
                    logger.info(f"获取行业板块成功: {len(sectors)}个板块")
                    return sectors
                else:
                    logger.error(f"获取行业板块失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"获取行业板块失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取行业板块出错: {str(e)}")
            return None

    def get_stocks_by_industry(self, industry_code: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        获取指定行业的股票列表

        Args:
            industry_code: 行业代码
            limit: 返回结果数量

        Returns:
            List[Dict]: 股票列表，失败返回None
        """
        try:
            url = f"https://xueqiu.com/hq/industry/stocklist.json"
            params = {
                "industryCode": industry_code,
                "page": 1,
                "size": limit
            }

            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("error_code") == 0:
                    stocks = result.get("data", {}).get("list", [])
                    logger.info(f"获取行业股票成功: {industry_code} ({len(stocks)}只股票)")
                    return stocks
                else:
                    logger.error(f"获取行业股票失败: {result.get('error_description')}")
                    return None
            else:
                logger.error(f"获取行业股票失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取行业股票出错: {str(e)}")
            return None


# 便捷函数
async def get_adapter() -> XueqiuAdapter:
    """获取雪球适配器实例（异步）"""
    from backend.utils.config import settings
    adapter = XueqiuAdapter(
        username=settings.xueqiu_username,
        password=settings.xueqiu_password
    )
    adapter.login()
    return adapter
