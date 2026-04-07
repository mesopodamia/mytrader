"""风险管理模块"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from backend.utils.config import settings


class RiskManager:
    """风险管理器"""
    
    def __init__(self):
        """初始化风险管理器"""
        self.max_position_ratio = settings.max_position_ratio
        self.daily_loss_limit = settings.daily_loss_limit
        self.trading_frequency_limit = settings.trading_frequency_limit
        
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.positions: Dict[str, Dict[str, Any]] = {}
    
    def check_position_limit(self, stock_code: str, new_position: float) -> bool:
        """
        检查持仓限制
        
        Args:
            stock_code: 股票代码
            new_position: 新增仓位
            
        Returns:
            bool: 是否允许
        """
        current_position = self.positions.get(stock_code, {}).get("ratio", 0)
        total_position = current_position + new_position
        
        if total_position > self.max_position_ratio:
            logger.warning(f"持仓超限: {stock_code} {total_position:.2%} > {self.max_position_ratio:.2%}")
            return False
        
        return True
    
    def check_daily_loss(self, potential_loss: float) -> bool:
        """
        检查日亏损限制
        
        Args:
            potential_loss: 潜在亏损
            
        Returns:
            bool: 是否允许
        """
        if self.daily_pnl - potential_loss < -self.daily_loss_limit:
            logger.warning(f"日亏损超限: {self.daily_pnl:.2%} - {potential_loss:.2%}")
            return False
        
        return True
    
    def check_trading_frequency(self) -> bool:
        """
        检查交易频率
        
        Returns:
            bool: 是否允许
        """
        if self.daily_trades >= self.trading_frequency_limit:
            logger.warning(f"交易频率超限: {self.daily_trades} >= {self.trading_frequency_limit}")
            return False
        
        return True
    
    def check_all(self, stock_code: str, new_position: float, potential_loss: float) -> Dict[str, Any]:
        """
        检查所有风险限制
        
        Args:
            stock_code: 股票代码
            new_position: 新增仓位
            potential_loss: 潜在亏损
            
        Returns:
            Dict: 检查结果
        """
        results = {
            "allowed": True,
            "checks": {}
        }
        
        # 检查持仓限制
        position_ok = self.check_position_limit(stock_code, new_position)
        results["checks"]["position_limit"] = {
            "passed": position_ok,
            "current": self.positions.get(stock_code, {}).get("ratio", 0),
            "new": new_position,
            "max": self.max_position_ratio
        }
        
        # 检查日亏损限制
        loss_ok = self.check_daily_loss(potential_loss)
        results["checks"]["daily_loss"] = {
            "passed": loss_ok,
            "current_pnl": self.daily_pnl,
            "potential_loss": potential_loss,
            "max_loss": self.daily_loss_limit
        }
        
        # 检查交易频率
        freq_ok = self.check_trading_frequency()
        results["checks"]["trading_frequency"] = {
            "passed": freq_ok,
            "current_trades": self.daily_trades,
            "max_trades": self.trading_frequency_limit
        }
        
        # 综合判断
        results["allowed"] = position_ok and loss_ok and freq_ok
        
        if not results["allowed"]:
            logger.warning(f"交易被拒绝: {stock_code}")
        
        return results
    
    def record_trade(self, pnl: float):
        """记录交易"""
        self.daily_trades += 1
        self.daily_pnl += pnl
        logger.info(f"交易记录: PnL {pnl:.2%}, 总PnL {self.daily_pnl:.2%}, 交易次数 {self.daily_trades}")
    
    def update_position(self, stock_code: str, ratio: float, price: float):
        """更新持仓"""
        self.positions[stock_code] = {
            "ratio": ratio,
            "price": price,
            "updated_at": datetime.now().isoformat()
        }
    
    def reset_daily(self):
        """重置每日数据"""
        self.daily_trades = 0
        self.daily_pnl = 0.0
        logger.info("每日数据重置")
    
    def get_risk_report(self) -> Dict[str, Any]:
        """获取风险报告"""
        total_position = sum(p.get("ratio", 0) for p in self.positions.values())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "daily_stats": {
                "trades": self.daily_trades,
                "pnl": self.daily_pnl,
                "limit": self.trading_frequency_limit
            },
            "positions": self.positions,
            "total_position": total_position,
            "max_position": self.max_position_ratio,
            "risk_level": "high" if total_position > self.max_position_ratio * 0.8 else "medium" if total_position > self.max_position_ratio * 0.5 else "low"
        }
