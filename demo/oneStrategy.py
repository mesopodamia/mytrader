from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # 用于管理日期时间
import os.path  # 来管理路径
import sys  # 用于找到脚本名称（argv[0]）

# 导入BackTrader平台
import backtrader as bt

# 创建一个策略
class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        '''此策略的日志记录功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存对收盘价线最新数据的引用
        self.dataclose = self.datas[0].close

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 做多/做空 订单 已提交/已执行 到/被代理 - 无事可做
            return

        # 检查订单是否已经完成
        # 注意：如果没有足够资金，代理可能拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 减记：没有挂单
        self.order = None

    def next(self):
        # 引用的收盘价的日志
        self.log('Close, %.2f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1]:
            # 当前收盘价小于前一K线收盘价

            if self.dataclose[-1] < self.dataclose[-2]:
                # 前一收盘价小于更前一收盘价

                # 买，买，买!!! (应用所有可能的默认参数)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()

if __name__ == '__main__':
    # 创建一个大脑实例
    cerebro = bt.Cerebro()

    # 添加一个策略
    cerebro.addstrategy(TestStrategy)

    # 数据保存在样本的一个子文件夹中。我们需要找到脚本的位置
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/yahoo-1996-2015.txt')

    # 创建一个数据槽
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # 不接收这个日期更早的数据
        fromdate=datetime.datetime(1996, 3, 1),
        # 不接收晚于这个日期的数据
        todate=datetime.datetime(2013, 12, 31),
        reverse=False)

    # 把数据槽添加到大脑引擎中
    cerebro.adddata(data)

    # 设定我们希望的初始金额
    cerebro.broker.setcash(100000.0)

    # 打印起始条件
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 运行所有命令
    cerebro.run()

    # 打印最终结果
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())