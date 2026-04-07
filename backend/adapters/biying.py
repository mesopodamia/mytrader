"""
必盈API 适配器

用于通过必盈API获取股票数据
"""
import time
import requests
from typing import Optional, Dict, List, Any
from loguru import logger
from datetime import datetime, timedelta


class BiyingAdapter:
    """必盈API 适配器"""

    def __init__(self):
        """初始化必盈API 适配器"""
        self.name = "biying"
        self.licence = "56D2EA0E-64AC-4753-A818-91FE278601BC"
        self.base_url = "https://api.biyingapi.com"
        logger.info("必盈API 适配器初始化成功")

    def _make_request(self, endpoint: str, params: dict = None) -> Optional[Dict[str, Any]]:
        """
        发送请求到必盈API

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            Dict: API 响应数据，失败返回None
        """
        try:
            url = f"{self.base_url}{endpoint}/{self.licence}"
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"必盈API 请求失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"必盈API 请求出错: {str(e)}")
            return None

    def get_stock_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取股票列表

        Returns:
            List[Dict]: 股票列表，失败返回None
        """
        try:
            data = self._make_request("/hslt/list")
            if data:
                stock_list = []
                for item in data:
                    stock_list.append({
                        "code": item["dm"],
                        "name": item["mc"],
                        "market": "沪市" if item["jys"] == "sh" else "深市"
                    })
                logger.info(f"获取股票列表成功: {len(stock_list)}只股票")
                return stock_list
            else:
                logger.error("获取股票列表失败: 无数据")
                return None
        except Exception as e:
            logger.error(f"获取股票列表出错: {str(e)}")
            return None

    def get_industry_sectors(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取行业板块列表

        Returns:
            List[Dict]: 行业板块列表，失败返回None
        """
        # 必盈API 没有直接提供行业板块列表接口，返回默认板块
        logger.info("必盈API 使用默认行业板块列表")
        return [
            {"code": "100", "name": "沪深300"},
            {"code": "101", "name": "中证500"},
            {"code": "102", "name": "创业板"}
        ]

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
            # 必盈API 没有直接提供行业股票列表接口，返回股票列表
            stock_list = self.get_stock_list()
            if stock_list:
                # 必盈API 返回的是所有股票，不需要限制数量
                logger.info(f"获取行业股票成功: {industry_code} ({len(stock_list)}只股票)")
                return stock_list
            else:
                logger.error("获取行业股票失败: 无数据")
                return None
        except Exception as e:
            logger.error(f"获取行业股票出错: {str(e)}")
            return None

    def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict: 股票行情数据，失败返回None
        """
        # 必盈API 没有提供实时行情接口，返回None
        logger.warning("必盈API 不支持实时行情接口")
        return None

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票信息

        Args:
            stock_code: 股票代码

        Returns:
            Dict: 股票信息，失败返回None
        """
        # 必盈API 没有提供股票信息接口，返回None
        logger.warning("必盈API 不支持股票信息接口")
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
            # 必盈API 没有提供搜索接口，从股票列表中过滤
            stock_list = self.get_stock_list()
            if stock_list:
                filtered_stocks = [
                    stock for stock in stock_list 
                    if keyword in stock["code"] or keyword in stock["name"]
                ][:limit]
                logger.info(f"搜索股票成功: {keyword} ({len(filtered_stocks)}条结果)")
                return filtered_stocks
            else:
                logger.error("搜索股票失败: 无数据")
                return None
        except Exception as e:
            logger.error(f"搜索股票出错: {str(e)}")
            return None

    def get_historical_data(self, stock_code: str, period: str = "1day", count: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        获取历史K线数据

        Args:
            stock_code: 股票代码
            period: 周期: 1day, 1week, 1month
            count: 数据条数

        Returns:
            List[Dict]: K线数据，失败返回None
        """
        # 必盈API 没有提供历史K线数据接口，返回None
        logger.warning("必盈API 不支持历史K线数据接口")
        return None
