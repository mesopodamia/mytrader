"""AI交易调度系统"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from backend.core.engine import AITradingEngine
from backend.utils.config import settings


class TradingScheduler:
    """交易调度系统"""
    
    def __init__(self):
        """初始化调度器"""
        self.engine = AITradingEngine()
        self.scheduler = AsyncIOScheduler()
        self.stock_list = settings.stock_list if hasattr(settings, 'stock_list') else ["000001", "600519", "000858"]
    
    def start(self):
        """启动调度器"""
        self._setup_trading_schedule()
        self.scheduler.start()
        logger.info("交易调度器启动")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("交易调度器停止")
    
    def _setup_trading_schedule(self):
        """设置交易计划"""
        # 每天开盘前分析
        self.scheduler.add_job(
            self._morning_analysis,
            CronTrigger(hour=8, minute=30),
            id="morning_analysis",
            name="早盘分析"
        )
        
        # 盘中每小时分析
        for hour in range(9, 15):
            self.scheduler.add_job(
                self._intraday_analysis,
                CronTrigger(hour=hour, minute=0),
                id=f"intraday_{hour}",
                name=f"盘中分析 {hour}:00"
            )
        
        # 每日收盘后总结
        self.scheduler.add_job(
            self._daily_summary,
            CronTrigger(hour=15, minute=30),
            id="daily_summary",
            name="收盘总结"
        )
    
    async def _morning_analysis(self):
        """早盘分析"""
        logger.info("开始早盘分析")
        result = await self.engine.run_pipeline(self.stock_list)
        
        if "decisions" in result:
            decisions = result["decisions"].get("decisions", {})
            await self.engine.execute_trades(decisions)
        
        logger.info("早盘分析完成")
    
    async def _intraday_analysis(self):
        """盘中分析"""
        logger.info("开始盘中分析")
        result = await self.engine.run_pipeline(self.stock_list)
        
        if "decisions" in result:
            decisions = result["decisions"].get("decisions", {})
            await self.engine.execute_trades(decisions)
        
        logger.info("盘中分析完成")
    
    async def _daily_summary(self):
        """收盘总结"""
        logger.info("开始收盘总结")
        
        # 生成日报
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "status": "market_closed"
        }
        
        logger.info(f"收盘总结: {summary}")
    
    async def run_once(self, stock_codes: Optional[List[str]] = None):
        """运行一次完整流程"""
        codes = stock_codes or self.stock_list
        return await self.engine.run_pipeline(codes)
    
    async def analyze_stock(self, stock_code: str) -> Dict[str, Any]:
        """分析单只股票"""
        return await self.engine.run_pipeline([stock_code])
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        jobs = self.scheduler.get_jobs()
        return {
            "status": "running" if self.scheduler.running else "stopped",
            "jobs": len(jobs),
            "next_run": jobs[0].next_run_time.isoformat() if jobs else None
        }
