"""数据采集Agent"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from backend.core.agents.base import BaseAgent
from backend.adapters.xueqiu import XueqiuAdapter
from backend.utils.config import settings


class DataCollectionAgent(BaseAgent):
    """数据采集Agent"""
    
    def __init__(self, name: str = "data_collector", description: str = "负责收集股票行情、新闻和基本面数据"):
        super().__init__(name, description)
        self.adapter = XueqiuAdapter(
            username=settings.xueqiu_username,
            password=settings.xueqiu_password
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行数据采集
        
        Args:
            input_data: 包含stock_codes等参数
            
        Returns:
            Dict: 采集的数据
        """
        try:
            stock_codes = input_data.get("stock_codes", [])
            if not stock_codes:
                return {"error": "No stock codes provided"}
            
            logger.info(f"开始采集数据: {stock_codes}")
            
            results = {}
            
            # 并发采集
            tasks = [
                self._collect_quotes(stock_codes),
                self._collect_historical_data(stock_codes),
                self._collect_stock_info(stock_codes)
            ]
            
            quotes, historical, stock_info = await asyncio.gather(*tasks)
            
            results["quotes"] = quotes
            results["historical"] = historical
            results["stock_info"] = stock_info
            results["timestamp"] = datetime.now().isoformat()
            
            self.update_memory("last_data", results)
            
            logger.info(f"数据采集完成: {len(stock_codes)} 只股票")
            return results
            
        except Exception as e:
            logger.error(f"数据采集失败: {str(e)}")
            return {"error": str(e)}
    
    async def _collect_quotes(self, stock_codes: List[str]) -> Optional[Dict[str, Any]]:
        """采集实时行情"""
        try:
            quotes = self.adapter.get_realtime_quotes(stock_codes)
            return quotes
        except Exception as e:
            logger.error(f"采集行情失败: {str(e)}")
            return None
    
    async def _collect_historical_data(self, stock_codes: List[str]) -> Dict[str, Any]:
        """采集历史数据"""
        historical = {}
        for code in stock_codes:
            try:
                data = self.adapter.get_historical_data(code, period="1day", count=30)
                if data:
                    historical[code] = data
            except Exception as e:
                logger.error(f"采集历史数据失败 {code}: {str(e)}")
        return historical
    
    async def _collect_stock_info(self, stock_codes: List[str]) -> Dict[str, Any]:
        """采集股票信息"""
        info = {}
        for code in stock_codes:
            try:
                data = self.adapter.get_stock_info(code)
                if data:
                    info[code] = data
            except Exception as e:
                logger.error(f"采集股票信息失败 {code}: {str(e)}")
        return info
