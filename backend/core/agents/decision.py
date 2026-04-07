"""决策Agent"""

from typing import Dict, List, Any
from datetime import datetime
from loguru import logger

from backend.core.agents.base import BaseAgent
from backend.utils.config import settings


class DecisionAgent(BaseAgent):
    """决策Agent - 综合分析结果并生成交易决策"""
    
    def __init__(self, name: str = "decision_maker", description: str = "综合技术面和基本面分析，生成交易决策"):
        super().__init__(name, description)
        self.max_position_ratio = settings.max_position_ratio
        self.daily_loss_limit = settings.daily_loss_limit
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行决策
        
        Args:
            input_data: 包含technical_analysis和fundamental_analysis
            
        Returns:
            Dict: 交易决策
        """
        try:
            technical = input_data.get("technical_analysis", {})
            fundamental = input_data.get("fundamental_analysis", {})
            
            decisions = {}
            
            for stock_code in technical.keys():
                decision = self._make_decision(stock_code, technical, fundamental)
                decisions[stock_code] = decision
            
            summary = self._generate_summary(decisions)
            
            result = {
                "decisions": decisions,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
            self.update_memory("last_decision", result)
            
            logger.info(f"决策生成完成: {len(decisions)} 只股票")
            return result
            
        except Exception as e:
            logger.error(f"决策生成失败: {str(e)}")
            return {"error": str(e)}
    
    def _make_decision(self, stock_code: str, technical: Dict, fundamental: Dict) -> Dict[str, Any]:
        """为单只股票生成决策"""
        tech_analysis = technical.get(stock_code, {})
        fund_analysis = fundamental.get(stock_code, {})
        
        # 评分系统
        scores = {
            "technical": self._score_technical(tech_analysis),
            "fundamental": self._score_fundamental(fund_analysis),
            "risk": self._score_risk(stock_code, tech_analysis)
        }
        
        total_score = sum(scores.values())
        
        # 决策逻辑
        if total_score >= 70:
            action = "buy"
            confidence = min(total_score / 100, 1.0)
            position_ratio = self.max_position_ratio * (total_score / 100)
        elif total_score >= 40:
            action = "hold"
            confidence = total_score / 100
            position_ratio = 0
        else:
            action = "sell"
            confidence = (100 - total_score) / 100
            position_ratio = 0
        
        return {
            "stock_code": stock_code,
            "action": action,
            "confidence": round(confidence, 2),
            "position_ratio": round(position_ratio, 2),
            "scores": scores,
            "reasons": self._generate_reasons(action, scores)
        }
    
    def _score_technical(self, tech: Dict) -> float:
        """技术面评分"""
        if not tech or "signals" not in tech:
            return 50
        
        signals = tech.get("signals", {})
        trend = tech.get("trend", {})
        
        score = 50
        
        # MA趋势
        if signals.get("ma_trend") == "bullish":
            score += 15
        elif signals.get("ma_trend") == "bearish":
            score -= 15
        
        # RSI
        rsi_signal = signals.get("rsi")
        if rsi_signal == "oversold":
            score += 20
        elif rsi_signal == "overbought":
            score -= 20
        
        # MACD
        if signals.get("macd") == "bullish":
            score += 10
        elif signals.get("macd") == "bearish":
            score -= 10
        
        # 趋势强度
        if trend.get("short_term") == "up":
            score += 10
        elif trend.get("short_term") == "down":
            score -= 10
        
        return max(0, min(100, score))
    
    def _score_fundamental(self, fund: Dict) -> float:
        """基本面评分"""
        if not fund:
            return 50
        
        valuation = fund.get("valuation", "fair")
        
        if valuation == "undervalued":
            return 80
        elif valuation == "overvalued":
            return 30
        return 50
    
    def _score_risk(self, stock_code: str, tech: Dict) -> float:
        """风险评分"""
        if not tech:
            return 50
        
        trend = tech.get("trend", {})
        volatility = trend.get("volatility")
        
        score = 50
        
        # 波动率
        if volatility and volatility > 0.05:
            score -= 20
        elif volatility and volatility < 0.02:
            score += 10
        
        return max(0, min(100, score))
    
    def _generate_reasons(self, action: str, scores: Dict) -> List[str]:
        """生成决策理由"""
        reasons = []
        
        if action == "buy":
            reasons.append("技术面看涨")
            reasons.append("估值合理")
        elif action == "sell":
            reasons.append("技术面看跌")
            reasons.append("估值偏高")
        else:
            reasons.append("维持现状")
        
        if scores.get("risk", 50) < 40:
            reasons.append("高风险警告")
        
        return reasons
    
    def _generate_summary(self, decisions: Dict) -> Dict[str, Any]:
        """生成决策摘要"""
        buy_count = sum(1 for d in decisions.values() if d.get("action") == "buy")
        sell_count = sum(1 for d in decisions.values() if d.get("action") == "sell")
        hold_count = sum(1 for d in decisions.values() if d.get("action") == "hold")
        
        avg_confidence = sum(d.get("confidence", 0) for d in decisions.values()) / len(decisions) if decisions else 0
        
        return {
            "total_stocks": len(decisions),
            "buy_recommendations": buy_count,
            "sell_recommendations": sell_count,
            "hold_recommendations": hold_count,
            "average_confidence": round(avg_confidence, 2),
            "timestamp": datetime.now().isoformat()
        }
