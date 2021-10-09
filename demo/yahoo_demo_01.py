from datetime import datetime
import backtrader as bt

#新建均线交叉的交易策略,快线是10周期，慢线是30周期
class SmaCross(bt.SignalStrategy):
    params = (('pfast', 10), ('pslow', 30),)
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.pfast), bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))

# 新建回测平台实例
cerebro = bt.Cerebro()

# 在线下载雅虎的特定时间段的股票行情信息
data = bt.feeds.YahooFinanceData(dataname='../datas/yahoo-1996-2015.txt', fromdate=datetime(2011, 1, 1),
                                 todate=datetime(2012, 12, 31))
# 添加刚刚获取的股票行情信息
cerebro.adddata(data)

# 添加交易策略（交易系统或交易方法）
cerebro.addstrategy(SmaCross)
# 运行交易回测
cerebro.run()
# 显示测试运行后的图表
cerebro.plot()