"""AI交易引擎"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from loguru import logger

from backend.core.agents.data import DataCollectionAgent
from backend.core.agents.analysis import TechnicalAnalysisAgent, FundamentalAnalysisAgent
from backend.core.agents.decision import DecisionAgent
from backend.adapters.xueqiu import XueqiuAdapter
from backend.utils.config import settings


class AITradingEngine:
    """AI交易引擎 - 协调所有Agent工作"""
    
    def __init__(self):
        """初始化引擎"""
        self.data_agent = DataCollectionAgent()
        self.tech_agent = TechnicalAnalysisAgent()
        self.fund_agent = FundamentalAnalysisAgent()
        self.decision_agent = DecisionAgent()
        self.adapter = XueqiuAdapter(
            username=settings.xueqiu_username,
            password=settings.xueqiu_password
        )
        self.stock_list = ["000001", "600519", "000858", "601318", "300750"]
    
    async def run_pipeline(self, stock_codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        运行完整交易流程
        
        Args:
            stock_codes: 股票代码列表，None使用默认列表
            
        Returns:
            Dict: 完整流程结果
        """
        try:
            codes = stock_codes or self.stock_list
            logger.info(f"开始AI交易流程: {codes}")
            
            # 1. 数据采集
            logger.info("步骤1: 数据采集")
            data_result = await self.data_agent.execute({"stock_codes": codes})
            
            if "error" in data_result:
                logger.error(f"数据采集失败: {data_result['error']}")
                return data_result
            
            # 2. 技术分析
            logger.info("步骤2: 技术分析")
            tech_result = await self.tech_agent.execute({
                "historical_data": data_result.get("historical", {})
            })
            
            # 3. 基本面分析
            logger.info("步骤3: 基本面分析")
            fund_result = await self.fund_agent.execute({
                "stock_info": data_result.get("stock_info", {})
            })
            
            # 4. 综合决策
            logger.info("步骤4: 综合决策")
            decision_input = {
                "technical_analysis": tech_result.get("technical_analysis", {}),
                "fundamental_analysis": fund_result.get("fundamental_analysis", {})
            }
            decision_result = await self.decision_agent.execute(decision_input)
            
            # 整合结果
            final_result = {
                "timestamp": datetime.now().isoformat(),
                "stocks_analyzed": codes,
                "data_collection": data_result,
                "technical_analysis": tech_result,
                "fundamental_analysis": fund_result,
                "decisions": decision_result,
                "summary": decision_result.get("summary", {})
            }
            
            logger.info("AI交易流程完成")
            return final_result
            
        except Exception as e:
            logger.error(f"AI交易流程失败: {str(e)}")
            return {"error": str(e)}
    
    async def execute_trades(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行交易
        
        Args:
            decisions: 决策结果
            
        Returns:
            Dict: 执行结果
        """
        try:
            if not self.adapter.login():
                return {"error": "登录失败"}
            
            portfolio_id = self._get_portfolio_id()
            if not portfolio_id:
                return {"error": "未找到组合"}
            
            results = []
            for stock_code, decision in decisions.items():
                if decision.get("action") == "buy":
                    result = self.adapter.place_order(
                        portfolio_id=portfolio_id,
                        stock_code=stock_code,
                        action="buy",
                        quantity=self._calculate_quantity(decision)
                    )
                    results.append({"stock": stock_code, "action": "buy", "result": result})
                elif decision.get("action") == "sell":
                    result = self.adapter.place_order(
                        portfolio_id=portfolio_id,
                        stock_code=stock_code,
                        action="sell",
                        quantity=self._calculate_quantity(decision)
                    )
                    results.append({"stock": stock_code, "action": "sell", "result": result})
            
            return {
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "total_trades": len(results)
            }
            
        except Exception as e:
            logger.error(f"交易执行失败: {str(e)}")
            return {"error": str(e)}
    
    def _get_portfolio_id(self) -> Optional[str]:
        """获取组合ID"""
        try:
            portfolios = self.adapter.get_portfolios()
            if portfolios:
                return portfolios[0].get("id")
            return None
        except Exception as e:
            logger.error(f"获取组合ID失败: {str(e)}")
            return None
    
    def _calculate_quantity(self, decision: Dict) -> int:
        """计算交易数量"""
        position_ratio = decision.get("position_ratio", 0)
        confidence = decision.get("confidence", 0)
        
        # 简单计算：根据仓位比例和置信度
        base_quantity = 100
        multiplier = int(position_ratio * 10 * confidence)
        return max(base_quantity, base_quantity * multiplier)
