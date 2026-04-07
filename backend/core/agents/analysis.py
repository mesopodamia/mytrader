"""分析Agent"""

from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger

from backend.core.agents.base import BaseAgent


class TechnicalAnalysisAgent(BaseAgent):
    """技术分析Agent"""
    
    def __init__(self, name: str = "technical_analyst", description: str = "负责技术指标分析和K线形态识别"):
        super().__init__(name, description)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技术分析
        
        Args:
            input_data: 包含historical_data等参数
            
        Returns:
            Dict: 分析结果
        """
        try:
            historical_data = input_data.get("historical_data", {})
            
            results = {}
            for stock_code, data in historical_data.items():
                analysis = self._analyze_stock(stock_code, data)
                results[stock_code] = analysis
            
            self.update_memory("last_analysis", results)
            
            logger.info(f"技术分析完成: {len(results)} 只股票")
            return {"technical_analysis": results, "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"技术分析失败: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_stock(self, stock_code: str, data: List[Dict]) -> Dict[str, Any]:
        """分析单只股票"""
        if not data:
            return {"error": "No data"}
        
        df = self._data_to_dataframe(data)
        
        # 计算技术指标
        indicators = self._calculate_indicators(df)
        
        # 生成信号
        signals = self._generate_signals(indicators)
        
        return {
            "stock_code": stock_code,
            "current_price": float(df['close'].iloc[-1]) if not df.empty else None,
            "indicators": indicators,
            "signals": signals,
            "trend": self._analyze_trend(df),
            "volume_analysis": self._analyze_volume(df)
        }
    
    def _data_to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """转换为DataFrame"""
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        return df
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算技术指标"""
        if df.empty:
            return {}
        
        # 移动平均线
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        # MACD
        df['ema12'] = df['close'].ewm(span=12).mean()
        df['ema26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return {
            "ma5": float(df['ma5'].iloc[-1]) if not df['ma5'].empty else None,
            "ma10": float(df['ma10'].iloc[-1]) if not df['ma10'].empty else None,
            "ma20": float(df['ma20'].iloc[-1]) if not df['ma20'].empty else None,
            "macd": float(df['macd'].iloc[-1]) if not df['macd'].empty else None,
            "macd_signal": float(df['macd_signal'].iloc[-1]) if not df['macd_signal'].empty else None,
            "rsi": float(df['rsi'].iloc[-1]) if not df['rsi'].empty else None,
        }
    
    def _generate_signals(self, indicators: Dict[str, Any]) -> Dict[str, str]:
        """生成交易信号"""
        signals = {}
        
        # MA信号
        if indicators.get('ma5') and indicators.get('ma10'):
            if indicators['ma5'] > indicators['ma10']:
                signals['ma_trend'] = 'bullish'
            else:
                signals['ma_trend'] = 'bearish'
        
        # RSI信号
        rsi = indicators.get('rsi')
        if rsi:
            if rsi > 70:
                signals['rsi'] = 'overbought'
            elif rsi < 30:
                signals['rsi'] = 'oversold'
            else:
                signals['rsi'] = 'neutral'
        
        # MACD信号
        if indicators.get('macd') and indicators.get('macd_signal'):
            if indicators['macd'] > indicators['macd_signal']:
                signals['macd'] = 'bullish'
            else:
                signals['macd'] = 'bearish'
        
        return signals
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """趋势分析"""
        if len(df) < 20:
            return {"error": "Insufficient data"}
        
        closes = df['close'].values
        prices_5d = closes[-5:] if len(closes) >= 5 else closes
        prices_10d = closes[-10:] if len(closes) >= 10 else closes
        prices_20d = closes[-20:] if len(closes) >= 20 else closes
        
        return {
            "short_term": self._trend_direction(prices_5d),
            "medium_term": self._trend_direction(prices_10d),
            "long_term": self._trend_direction(prices_20d),
            "volatility": float(np.std(closes[-30:])) if len(closes) >= 30 else None
        }
    
    def _trend_direction(self, prices: np.ndarray) -> str:
        """判断趋势方向"""
        if len(prices) < 2:
            return "neutral"
        
        slope = (prices[-1] - prices[0]) / prices[0]
        if slope > 0.02:
            return "up"
        elif slope < -0.02:
            return "down"
        return "sideways"
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """量能分析"""
        if df.empty:
            return {"error": "No data"}
        
        volumes = df['volume'].values
        avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
        current_volume = volumes[-1] if len(volumes) > 0 else 0
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        return {
            "average_volume": float(avg_volume),
            "current_volume": float(current_volume),
            "volume_ratio": float(volume_ratio),
            "volume_trend": "increasing" if volume_ratio > 1.5 else "decreasing" if volume_ratio < 0.5 else "normal"
        }


class FundamentalAnalysisAgent(BaseAgent):
    """基本面分析Agent"""
    
    def __init__(self, name: str = "fundamental_analyst", description: str = "负责财务数据和行业分析"):
        super().__init__(name, description)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行基本面分析
        
        Args:
            input_data: 包含stock_info等参数
            
        Returns:
            Dict: 分析结果
        """
        try:
            stock_info = input_data.get("stock_info", {})
            
            results = {}
            for stock_code, info in stock_info.items():
                analysis = self._analyze_stock(stock_code, info)
                results[stock_code] = analysis
            
            self.update_memory("last_analysis", results)
            
            logger.info(f"基本面分析完成: {len(results)} 只股票")
            return {"fundamental_analysis": results, "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"基本面分析失败: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_stock(self, stock_code: str, info: Dict) -> Dict[str, Any]:
        """分析单只股票"""
        if not info:
            return {"error": "No data"}
        
        fundamental = info.get("fundamental", {})
        
        return {
            "stock_code": stock_code,
            "pe_ratio": fundamental.get("pe_ttm"),
            "pb_ratio": fundamental.get("pb"),
            "dividend_yield": fundamental.get("dividend_yield_ttm"),
            "roce": fundamental.get("roce"),
            "net_profit_margin": fundamental.get("net_profit_margin"),
            "debt_to_asset": fundamental.get("debt_to_asset"),
            "growth_rate": self._analyze_growth(fundamental),
            "valuation": self._evaluate_valuation(fundamental)
        }
    
    def _analyze_growth(self, fundamental: Dict) -> Dict[str, Any]:
        """分析成长性"""
        return {
            "revenue_growth": fundamental.get("revenue_growth"),
            "profit_growth": fundamental.get("profit_growth"),
            "asset_growth": fundamental.get("asset_growth")
        }
    
    def _evaluate_valuation(self, fundamental: Dict) -> str:
        """估值评估"""
        pe = fundamental.get("pe_ttm")
        pb = fundamental.get("pb")
        
        if not pe or not pb:
            return "unknown"
        
        if pe < 15 and pb < 2:
            return "undervalued"
        elif pe > 40 or pb > 5:
            return "overvalued"
        return "fair"
