"""回测模块"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

from backend.utils.config import settings


class Backtester:
    """回测器"""
    
    def __init__(self, initial_capital: float = 1000000.0):
        """
        初始化回测器
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
    
    def load_historical_data(self, stock_code: str, data: List[Dict]) -> pd.DataFrame:
        """
        加载历史数据
        
        Args:
            stock_code: 股票代码
            data: 历史数据
            
        Returns:
            DataFrame: 处理后的数据
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        
        return df
    
    def run_backtest(
        self,
        stock_data: Dict[str, List[Dict]],
        signals: Dict[str, List[Dict]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            stock_data: 股票历史数据
            signals: 交易信号
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 回测结果
        """
        try:
            logger.info("开始回测")
            
            # 初始化
            self.capital = self.initial_capital
            self.positions = {}
            self.trades = []
            self.equity_curve = []
            
            # 合并所有数据
            all_dates = set()
            for data in stock_data.values():
                for record in data:
                    all_dates.add(record['time'])
            
            dates = sorted(all_dates)
            
            # 回测循环
            for date in dates:
                self._process_day(date, stock_data, signals)
            
            # 计算绩效指标
            metrics = self._calculate_metrics()
            
            result = {
                "start_date": start_date or dates[0] if dates else None,
                "end_date": end_date or dates[-1] if dates else None,
                "initial_capital": self.initial_capital,
                "final_capital": self.capital,
                "total_return": (self.capital - self.initial_capital) / self.initial_capital,
                "metrics": metrics,
                "trades": self.trades,
                "equity_curve": self.equity_curve
            }
            
            logger.info(f"回测完成: 总收益 {result['total_return']:.2%}")
            return result
            
        except Exception as e:
            logger.error(f"回测失败: {str(e)}")
            return {"error": str(e)}
    
    def _process_day(
        self,
        date: str,
        stock_data: Dict[str, List[Dict]],
        signals: Dict[str, List[Dict]]
    ):
        """处理单日交易"""
        # 执行信号
        for stock_code, stock_signals in signals.items():
            signal = next((s for s in stock_signals if s['time'] == date), None)
            
            if signal:
                self._execute_signal(stock_code, signal, stock_data.get(stock_code, []))
        
        # 记录当日净值
        self._record_equity(date)
    
    def _execute_signal(self, stock_code: str, signal: Dict, data: List[Dict]):
        """执行交易信号"""
        if not data:
            return
        
        # 获取最新价格
        latest_price = data[-1].get('close', 0) if data else 0
        
        action = signal.get('action')
        quantity = signal.get('quantity', 100)
        
        if action == 'buy':
            cost = latest_price * quantity
            if self.capital >= cost:
                self.capital -= cost
                if stock_code in self.positions:
                    self.positions[stock_code]['quantity'] += quantity
                    self.positions[stock_code]['cost'] = (
                        self.positions[stock_code]['cost'] * (self.positions[stock_code]['quantity'] - quantity) + cost
                    ) / self.positions[stock_code]['quantity']
                else:
                    self.positions[stock_code] = {
                        'quantity': quantity,
                        'cost': latest_price,
                        'bought_at': signal.get('time')
                    }
                
                self.trades.append({
                    'date': signal.get('time'),
                    'stock': stock_code,
                    'action': 'buy',
                    'price': latest_price,
                    'quantity': quantity,
                    'cost': cost
                })
        
        elif action == 'sell':
            if stock_code in self.positions and self.positions[stock_code]['quantity'] >= quantity:
                revenue = latest_price * quantity
                self.capital += revenue
                
                position = self.positions[stock_code]
                cost = position['cost'] * quantity
                pnl = revenue - cost
                
                position['quantity'] -= quantity
                if position['quantity'] == 0:
                    del self.positions[stock_code]
                
                self.trades.append({
                    'date': signal.get('time'),
                    'stock': stock_code,
                    'action': 'sell',
                    'price': latest_price,
                    'quantity': quantity,
                    'revenue': revenue,
                    'pnl': pnl
                })
    
    def _record_equity(self, date: str):
        """记录当日净值"""
        position_value = sum(
            p['quantity'] * self._get_current_price(p, date)
            for p in self.positions.values()
        )
        
        self.equity_curve.append({
            'date': date,
            'capital': self.capital,
            'position_value': position_value,
            'total_value': self.capital + position_value
        })
    
    def _get_current_price(self, position: Dict, date: str) -> float:
        """获取当前价格"""
        # 简化处理，实际应从数据中获取
        return position.get('cost', 0)
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """计算绩效指标"""
        if not self.equity_curve:
            return {}
        
        total_values = [e['total_value'] for e in self.equity_curve]
        
        # 收益率
        returns = [(total_values[i] - total_values[i-1]) / total_values[i-1] 
                   for i in range(1, len(total_values))]
        
        # 绩效指标
        total_return = (total_values[-1] - total_values[0]) / total_values[0]
        
        if returns:
            daily_returns = pd.Series(returns)
            sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() > 0 else 0
            max_drawdown = self._calculate_max_drawdown(total_values)
        else:
            sharpe_ratio = 0
            max_drawdown = 0
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": self._calculate_win_rate(),
            "total_trades": len(self.trades),
            "profit_trades": sum(1 for t in self.trades if t.get('pnl', 0) > 0),
            "loss_trades": sum(1 for t in self.trades if t.get('pnl', 0) < 0)
        }
    
    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """计算最大回撤"""
        if len(values) < 2:
            return 0
        
        max_value = values[0]
        max_drawdown = 0
        
        for value in values:
            if value > max_value:
                max_value = value
            drawdown = (max_value - value) / max_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def _calculate_win_rate(self) -> float:
        """计算胜率"""
        if not self.trades:
            return 0
        
        wins = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        return wins / len(self.trades)
