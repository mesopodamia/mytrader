from jqdata import *

def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')

    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
      # 开盘前运行
    # run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
      # 开盘时运行
    run_daily(market_open, time='open', reference_security='000300.XSHG')
      # 收盘后运行
    # run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')

def market_open(context):
    log.info('函数运行时间(market_open):'+str(context.current_dt.time()))
    security = g.security
    # 取得上一时间点价格
    current_price = close_data['close'][-1]
    # 取得当前的现金
    cash = context.portfolio.available_cash

    # 判断是否空仓
    if (short_positions_dict.values() == None):
        empty_position = True
    else:
        empty_position = False

    # 价格低于13.85, 清仓
    if (current_price < 13.85) and (empty_position == False):
        order_target(security, 0)
        log.info("价格低于13.85, 卖出所有仓位 %s" % (security))

    if (current_price < 13.97) and (empty_position == False):
        order_value(security, cash)
        log.info("半仓情况，价格低于14.4, 买入全仓 %s" % (security))


    if (current_price < 14.4):
        if (empty_position == True):
            order_value(security, (cash/2))
            log.info("空仓情况，价格低于14.4, 买入半仓 %s" % (security))
        else:
            order_value(security, cash)
            log.info("半仓情况，价格低于14.4, 买入全仓 %s" % (security))


