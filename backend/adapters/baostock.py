"""
Baostock 适配器

用于通过 Baostock 库获取股票数据
"""
import time
from typing import Optional, Dict, List, Any
from loguru import logger
import baostock as bs
from datetime import datetime, timedelta


class BaostockAdapter:
    """Baostock 适配器"""

    def __init__(self):
        """初始化 Baostock 适配器"""
        self.name = "baostock"
        self.initialized = False
        self._init_baostock()
        logger.info("Baostock 适配器初始化成功")

    def _init_baostock(self):
        """初始化 Baostock 连接"""
        try:
            lg = bs.login()
            if lg.error_code == '0':
                self.initialized = True
                logger.info("Baostock 登录成功")
            else:
                logger.error(f"Baostock 登录失败: {lg.error_msg}")
                self.initialized = False
        except Exception as e:
            logger.error(f"Baostock 初始化出错: {str(e)}")
            self.initialized = False

    def _ensure_initialized(self):
        """确保 Baostock 已初始化"""
        if not self.initialized:
            self._init_baostock()
        return self.initialized

    def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict: 股票行情数据，失败返回None
        """
        if not self._ensure_initialized():
            logger.error("Baostock 未初始化，无法获取实时行情")
            return None

        try:
            # 构建 Baostock 格式的股票代码列表
            bs_codes = []
            for code in stock_codes:
                if code.startswith("6"):
                    bs_codes.append(f"sh.{code}")
                else:
                    bs_codes.append(f"sz.{code}")

            # 使用 Baostock 获取实时行情
            rs = bs.query_realtime_stock_data(code=','.join(bs_codes))
            if rs.error_code == '0':
                result = {}
                while (rs.error_code == '0') & rs.next():
                    row = rs.get_row_data()
                    code = row[0].replace("sh.", "").replace("sz.", "")
                    result[code] = {
                        "code": code,
                        "name": row[1],
                        "current": float(row[3]) if row[3] else 0,
                        "change": float(row[4]) if row[4] else 0,
                        "change_percent": float(row[5]) if row[5] else 0,
                        "open": float(row[6]) if row[6] else 0,
                        "high": float(row[7]) if row[7] else 0,
                        "low": float(row[8]) if row[8] else 0,
                        "volume": int(row[9]) if row[9] else 0,
                        "amount": float(row[10]) if row[10] else 0,
                        "time": row[11]
                    }
                if result:
                    logger.info(f"获取实时行情成功: {len(result)}只股票")
                    return result
                else:
                    logger.error("获取实时行情失败: 无数据")
                    return None
            else:
                logger.error(f"获取实时行情失败: {rs.error_msg}")
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
        if not self._ensure_initialized():
            logger.error("Baostock 未初始化，无法获取股票信息")
            return None

        try:
            # 构建 Baostock 格式的股票代码
            if stock_code.startswith("6"):
                bs_code = f"sh.{stock_code}"
            else:
                bs_code = f"sz.{stock_code}"

            # 使用 Baostock 获取股票实时数据
            rs = bs.query_realtime_stock_data(code=bs_code)
            if rs.error_code == '0':
                if rs.next():
                    row = rs.get_row_data()
                    info = {
                        "code": stock_code,
                        "name": row[1],
                        "current": float(row[3]) if row[3] else 0,
                        "open": float(row[6]) if row[6] else 0,
                        "high": float(row[7]) if row[7] else 0,
                        "low": float(row[8]) if row[8] else 0,
                        "prev_close": float(row[2]) if row[2] else 0,
                        "volume": int(row[9]) if row[9] else 0,
                        "amount": float(row[10]) if row[10] else 0,
                        "time": row[11]
                    }
                    logger.info(f"获取股票信息成功: {stock_code}")
                    return info
                else:
                    logger.error(f"获取股票信息失败: 未找到股票 {stock_code}")
                    return None
            else:
                logger.error(f"获取股票信息失败: {rs.error_msg}")
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
        if not self._ensure_initialized():
            logger.error("Baostock 未初始化，无法搜索股票")
            return None

        try:
            # 使用 Baostock 获取所有股票列表
            rs = bs.query_stock_basic()
            if rs.error_code == '0':
                stock_list = []
                while (rs.error_code == '0') & rs.next():
                    row = rs.get_row_data()
                    code = row[0].replace("sh.", "").replace("sz.", "")
                    name = row[1]
                    if keyword in code or keyword in name:
                        stock_list.append({
                            "code": code,
                            "name": name,
                            "market": "沪市" if code.startswith("6") else "深市"
                        })
                        if len(stock_list) >= limit:
                            break
                
                if stock_list:
                    logger.info(f"搜索股票成功: {keyword} ({len(stock_list)}条结果)")
                    return stock_list
                else:
                    logger.error("搜索股票失败: 无结果")
                    return None
            else:
                logger.error(f"搜索股票失败: {rs.error_msg}")
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
        if not self._ensure_initialized():
            logger.error("Baostock 未初始化，无法获取行业板块")
            return None

        try:
            # 使用 Baostock 获取行业板块列表
            rs = bs.query_stock_industry()
            if rs.error_code == '0':
                sectors = {}
                while (rs.error_code == '0') & rs.next():
                    row = rs.get_row_data()
                    industry = row[2]
                    if industry not in sectors:
                        sectors[industry] = {
                            "code": industry,
                            "name": industry
                        }
                
                sector_list = list(sectors.values())
                if sector_list:
                    logger.info(f"获取行业板块成功: {len(sector_list)}个板块")
                    return sector_list
                else:
                    logger.error("获取行业板块失败: 无数据")
                    return None
            else:
                logger.error(f"获取行业板块失败: {rs.error_msg}")
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
        if not self._ensure_initialized():
            logger.error("Baostock 未初始化，无法获取行业股票")
            return None

        try:
            # 使用 Baostock 获取行业股票列表
            rs = bs.query_stock_industry()
            if rs.error_code == '0':
                stock_list = []
                while (rs.error_code == '0') & rs.next():
                    row = rs.get_row_data()
                    if row[2] == industry_code:
                        code = row[0].replace("sh.", "").replace("sz.", "")
                        stock_list.append({
                            "code": code,
                            "name": row[1],
                            "market": "沪市" if code.startswith("6") else "深市"
                        })
                        if len(stock_list) >= limit:
                            break
                
                if stock_list:
                    logger.info(f"获取行业股票成功: {industry_code} ({len(stock_list)}只股票)")
                    return stock_list
                else:
                    logger.error("获取行业股票失败: 无数据")
                    return None
            else:
                logger.error(f"获取行业股票失败: {rs.error_msg}")
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
        if not self._ensure_initialized():
            logger.error("Baostock 未初始化，无法获取历史K线数据")
            return None

        try:
            # 构建 Baostock 格式的股票代码
            if stock_code.startswith("6"):
                bs_code = f"sh.{stock_code}"
            else:
                bs_code = f"sz.{stock_code}"

            # 计算起始日期
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=count * 2)).strftime("%Y-%m-%d")

            # 转换周期
            if period == "1day":
                frequency = "d"
            elif period == "1week":
                frequency = "w"
            elif period == "1month":
                frequency = "m"
            else:
                frequency = "d"

            # 使用 Baostock 获取历史K线数据
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,volume,amount",
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjustflag="3"
            )

            if rs.error_code == '0':
                kline_data = []
                while (rs.error_code == '0') & rs.next():
                    row = rs.get_row_data()
                    kline_data.append({
                        "date": row[0],
                        "open": float(row[1]) if row[1] else 0,
                        "high": float(row[2]) if row[2] else 0,
                        "low": float(row[3]) if row[3] else 0,
                        "close": float(row[4]) if row[4] else 0,
                        "volume": int(row[5]) if row[5] else 0,
                        "amount": float(row[6]) if row[6] else 0
                    })
                
                if kline_data:
                    logger.info(f"获取历史K线数据成功: {stock_code} ({len(kline_data)}条)")
                    return kline_data
                else:
                    logger.error("获取历史K线数据失败: 无数据")
                    return None
            else:
                logger.error(f"获取历史K线数据失败: {rs.error_msg}")
                return None

        except Exception as e:
            logger.error(f"获取历史K线数据出错: {str(e)}")
            return None

    def __del__(self):
        """析构函数，关闭 Baostock 连接"""
        try:
            if self.initialized:
                bs.logout()
                logger.info("Baostock 已登出")
        except Exception as e:
            logger.error(f"Baostock 登出出错: {str(e)}")
