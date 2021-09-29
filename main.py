from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import datetime
import os.path
import sys

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'datas\\yahoo-1996-2015.txt')

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # 不接收这个日期更早的数据
        fromdate=datetime.datetime(2000, 1, 1),
        # 不接收晚于这个日期的数据
        todate=datetime.datetime(2000, 12, 31),
        reverse=False)

    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())