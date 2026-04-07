"""
AKShare 适配器

用于通过 AKShare 库获取股票数据
"""
import time
from typing import Optional, Dict, List, Any
from loguru import logger
import akshare as ak
from datetime import datetime, timedelta


class AKShareAdapter:
    """AKShare 适配器"""

    def __init__(self):
        """初始化 AKShare 适配器"""
        self.name = "akshare"
        logger.info("AKShare 适配器初始化成功")

    def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[Dict[str, Any]]:
        """
        获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict: 股票行情数据，失败返回None
        """
        try:
            # 构建 AKShare 格式的股票代码列表
            ak_codes = []
            for code in stock_codes:
                if code.startswith("6"):
                    ak_codes.append(f"sh{code}")
                else:
                    ak_codes.append(f"sz{code}")

            # 使用 AKShare 获取实时行情
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                result = {}
                for _, row in df.iterrows():
                    code = row['代码']
                    if code in ak_codes:
                        result[code] = {
                            "code": code.replace("sh", "").replace("sz", ""),
                            "name": row['名称'],
                            "current": float(row['最新价']),
                            "change": float(row['涨跌额']),
                            "change_percent": float(row['涨跌幅']),
                            "open": float(row['开盘价']),
                            "high": float(row['最高价']),
                            "low": float(row['最低价']),
                            "volume": int(row['成交量']),
                            "amount": float(row['成交额']),
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                if result:
                    logger.info(f"获取实时行情成功: {len(result)}只股票")
                    return result
                else:
                    logger.error("获取实时行情失败: 无数据")
                    return None
            else:
                logger.error("获取实时行情失败: 无数据")
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
            # 使用 AKShare 获取股票实时数据
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                # 构建 AKShare 格式的股票代码
                if stock_code.startswith("6"):
                    ak_code = f"sh{stock_code}"
                else:
                    ak_code = f"sz{stock_code}"

                # 查找对应股票
                stock_data = df[df['代码'] == ak_code]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    info = {
                        "code": stock_code,
                        "name": row['名称'],
                        "current": float(row['最新价']),
                        "open": float(row['开盘价']),
                        "high": float(row['最高价']),
                        "low": float(row['最低价']),
                        "prev_close": float(row['昨收价']),
                        "volume": int(row['成交量']),
                        "amount": float(row['成交额']),
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    logger.info(f"获取股票信息成功: {stock_code}")
                    return info
                else:
                    logger.error(f"获取股票信息失败: 未找到股票 {stock_code}")
                    return None
            else:
                logger.error("获取股票信息失败: 无数据")
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
            # 使用 AKShare 获取所有股票列表
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                # 筛选包含关键词的股票
                filtered = df[
                    (df['代码'].str.contains(keyword)) | 
                    (df['名称'].str.contains(keyword))
                ]
                
                stock_list = []
                for _, row in filtered.head(limit).iterrows():
                    code = row['代码'].replace("sh", "").replace("sz", "")
                    stock_list.append({
                        "code": code,
                        "name": row['名称'],
                        "market": "沪市" if code.startswith("6") else "深市"
                    })
                
                if stock_list:
                    logger.info(f"搜索股票成功: {keyword} ({len(stock_list)}条结果)")
                    return stock_list
                else:
                    logger.error("搜索股票失败: 无结果")
                    return None
            else:
                logger.error("搜索股票失败: 无数据")
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
        max_retries = 3
        for retry in range(max_retries):
            try:
                # 使用 AKShare 获取行业板块列表
                df = ak.stock_board_industry_name_em()
                if df is not None and not df.empty:
                    sector_list = []
                    for _, row in df.iterrows():
                        sector_list.append({
                            "code": row['板块代码'],
                            "name": row['板块名称']
                        })
                    
                    if sector_list:
                        logger.info(f"获取行业板块成功: {len(sector_list)}个板块")
                        return sector_list
                    else:
                        logger.error("获取行业板块失败: 无数据")
                        return None
                else:
                    logger.error("获取行业板块失败: 无数据")
                    return None

            except Exception as e:
                logger.error(f"获取行业板块出错 (尝试 {retry + 1}/{max_retries}): {str(e)}")
                if retry < max_retries - 1:
                    logger.info(f"等待 2 秒后重试...")
                    time.sleep(2)
                else:
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
        max_retries = 3
        for retry in range(max_retries):
            try:
                # 使用 AKShare 获取行业股票列表
                df = ak.stock_board_industry_cons_em(symbol=industry_code)
                if df is not None and not df.empty:
                    stock_list = []
                    for _, row in df.head(limit).iterrows():
                        code = row['代码']
                        stock_list.append({
                            "code": code,
                            "name": row['名称'],
                            "market": "沪市" if code.startswith("6") else "深市"
                        })
                    
                    if stock_list:
                        logger.info(f"获取行业股票成功: {industry_code} ({len(stock_list)}只股票)")
                        return stock_list
                    else:
                        logger.error("获取行业股票失败: 无数据")
                        return None
                else:
                    logger.error("获取行业股票失败: 无数据")
                    return None

            except Exception as e:
                logger.error(f"获取行业股票出错 (尝试 {retry + 1}/{max_retries}): {str(e)}")
                if retry < max_retries - 1:
                    logger.info(f"等待 2 秒后重试...")
                    time.sleep(2)
                else:
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
            # 构建 AKShare 格式的股票代码
            if stock_code.startswith("6"):
                ak_code = f"sh{stock_code}"
            else:
                ak_code = f"sz{stock_code}"

            # 使用 AKShare 获取历史K线数据
            if period == "1day":
                df = ak.stock_zh_a_hist(symbol=ak_code, period="daily", adjust="qfq")
            elif period == "1week":
                df = ak.stock_zh_a_hist(symbol=ak_code, period="weekly", adjust="qfq")
            elif period == "1month":
                df = ak.stock_zh_a_hist(symbol=ak_code, period="monthly", adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=ak_code, period="daily", adjust="qfq")

            if df is not None and not df.empty:
                kline_data = []
                for _, row in df.tail(count).iterrows():
                    kline_data.append({
                        "date": row['日期'],
                        "open": float(row['开盘']),
                        "high": float(row['最高']),
                        "low": float(row['最低']),
                        "close": float(row['收盘']),
                        "volume": int(row['成交量']),
                        "amount": float(row['成交额'])
                    })
                
                if kline_data:
                    logger.info(f"获取历史K线数据成功: {stock_code} ({len(kline_data)}条)")
                    return kline_data
                else:
                    logger.error("获取历史K线数据失败: 无数据")
                    return None
            else:
                logger.error("获取历史K线数据失败: 无数据")
                return None

        except Exception as e:
            logger.error(f"获取历史K线数据出错: {str(e)}")
            return None
