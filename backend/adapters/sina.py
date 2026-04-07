"""
新浪财经适配器

用于从新浪财经获取股票数据
"""
import time
from typing import Optional, Dict, List, Any
from loguru import logger
import requests
from datetime import datetime, timedelta


class SinaAdapter:
    """新浪财经适配器"""

    def __init__(self):
        """初始化新浪财经适配器"""
        self.base_url = "https://hq.sinajs.cn"
        self.api_url = "https://finance.sina.com.cn"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://finance.sina.com.cn/",
        }

    def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict: 股票行情数据，失败返回None
        """
        try:
            # 新浪财经股票代码格式：sh600000 或 sz000001
            sina_codes = []
            for code in stock_codes:
                if code.startswith("6"):
                    sina_codes.append(f"sh{code}")
                else:
                    sina_codes.append(f"sz{code}")

            # 构建请求URL
            code_str = ",".join(sina_codes)
            url = f"{self.base_url}?list={code_str}"

            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                result = {}
                lines = response.text.strip().split("\n")
                for line in lines:
                    if line:
                        try:
                            # 解析新浪财经返回的数据格式
                            # var hq_str_sh600000="浦发银行,10.00,10.01,9.99,10.02,9.98,9.99,9.99,10000,100000,100,9.98,100,9.97,100,9.96,100,9.95,100,9.94,100,10.00,100,10.01,100,10.02,100,10.03,100,10.04,100,2024-01-01,15:00:00,0"
                            code = line.split("=")[0].split("_")[1]
                            data = line.split("=")[1].strip('"').split(",")
                            if len(data) >= 32:
                                result[code] = {
                                    "code": code.replace("sh", "").replace("sz", ""),
                                    "name": data[0],
                                    "current": float(data[3]),
                                    "change": float(data[3]) - float(data[2]),
                                    "change_percent": (float(data[3]) - float(data[2])) / float(data[2]) * 100,
                                    "open": float(data[1]),
                                    "high": float(data[4]),
                                    "low": float(data[5]),
                                    "volume": int(data[8]),
                                    "amount": float(data[9]),
                                    "time": f"{data[30]} {data[31]}"
                                }
                        except Exception as e:
                            logger.error(f"解析新浪财经数据失败: {str(e)}")
                if result:
                    logger.info(f"获取实时行情成功: {len(result)}只股票")
                    return result
                else:
                    logger.error("获取实时行情失败: 无数据")
                    return None
            else:
                logger.error(f"获取实时行情失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取实时行情出错: {str(e)}")
            return None

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票信息

        Args:
            stock_code: 股票代码

        Returns:
            Dict: 股票信息，失败返回None
        """
        try:
            # 新浪财经股票代码格式：sh600000 或 sz000001
            if stock_code.startswith("6"):
                sina_code = f"sh{stock_code}"
            else:
                sina_code = f"sz{stock_code}"

            # 构建请求URL
            url = f"{self.base_url}?list={sina_code}"

            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                lines = response.text.strip().split("\n")
                for line in lines:
                    if line:
                        try:
                            # 解析新浪财经返回的数据格式
                            data = line.split("=")[1].strip('"').split(",")
                            if len(data) >= 32:
                                info = {
                                    "code": stock_code,
                                    "name": data[0],
                                    "current": float(data[3]),
                                    "open": float(data[1]),
                                    "high": float(data[4]),
                                    "low": float(data[5]),
                                    "prev_close": float(data[2]),
                                    "volume": int(data[8]),
                                    "amount": float(data[9]),
                                    "time": f"{data[30]} {data[31]}"
                                }
                                logger.info(f"获取股票信息成功: {stock_code}")
                                return info
                        except Exception as e:
                            logger.error(f"解析新浪财经数据失败: {str(e)}")
                logger.error("获取股票信息失败: 无数据")
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
            # 新浪财经搜索API
            url = f"{self.api_url}/stock/search/"
            params = {
                "q": keyword,
                "t": "all",
                "c": "1"
            }

            response = self.session.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                # 解析HTML页面，提取股票信息
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                stock_list = []

                # 查找股票列表
                stock_items = soup.find_all("div", class_="list_item")
                for item in stock_items[:limit]:
                    try:
                        code_elem = item.find("span", class_="code")
                        name_elem = item.find("span", class_="name")
                        if code_elem and name_elem:
                            code = code_elem.text.strip()
                            name = name_elem.text.strip()
                            stock_list.append({
                                "code": code,
                                "name": name,
                                "market": "A股" if code.startswith("6") or code.startswith("0") or code.startswith("3") else "其他"
                            })
                    except Exception as e:
                        logger.error(f"解析搜索结果失败: {str(e)}")

                if stock_list:
                    logger.info(f"搜索股票成功: {keyword} ({len(stock_list)}条结果)")
                    return stock_list
                else:
                    logger.error("搜索股票失败: 无结果")
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
            # 新浪财经行业板块API
            url = f"{self.api_url}/stock/industry/"

            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                # 解析HTML页面，提取行业板块信息
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                sector_list = []

                # 查找行业板块列表
                sector_items = soup.find_all("a", class_="industry")
                for item in sector_items[:50]:  # 限制返回数量
                    try:
                        name = item.text.strip()
                        href = item.get("href")
                        # 提取行业代码
                        code = href.split("/")[-1].split(".")[0]
                        sector_list.append({
                            "code": code,
                            "name": name
                        })
                    except Exception as e:
                        logger.error(f"解析行业板块失败: {str(e)}")

                if sector_list:
                    logger.info(f"获取行业板块成功: {len(sector_list)}个板块")
                    return sector_list
                else:
                    logger.error("获取行业板块失败: 无数据")
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
            # 新浪财经行业股票API
            url = f"{self.api_url}/stock/industry/{industry_code}.shtml"

            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                # 解析HTML页面，提取股票信息
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                stock_list = []

                # 查找股票列表
                stock_items = soup.find_all("tr", class_="" )
                for item in stock_items[:limit]:
                    try:
                        td_elems = item.find_all("td")
                        if len(td_elems) >= 2:
                            code = td_elems[0].text.strip()
                            name = td_elems[1].text.strip()
                            stock_list.append({
                                "code": code,
                                "name": name,
                                "market": "A股" if code.startswith("6") or code.startswith("0") or code.startswith("3") else "其他"
                            })
                    except Exception as e:
                        logger.error(f"解析行业股票失败: {str(e)}")

                if stock_list:
                    logger.info(f"获取行业股票成功: {industry_code} ({len(stock_list)}只股票)")
                    return stock_list
                else:
                    logger.error("获取行业股票失败: 无数据")
                    return None
            else:
                logger.error(f"获取行业股票失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"获取行业股票出错: {str(e)}")
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
        try:
            # 新浪财经历史数据API
            # 注意：新浪财经的历史数据API可能需要特定的参数格式
            # 这里使用一个简化的实现
            logger.warning("新浪财经适配器暂不支持历史K线数据")
            return None

        except Exception as e:
            logger.error(f"获取历史数据出错: {str(e)}")
            return None
