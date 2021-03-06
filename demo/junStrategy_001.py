from jqdata import *

def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
    run_daily(market_open, time='open', reference_security='000300.XSHG')

def before_market_open(context):
    log.info('函数运行时间(before_market_open)：'+str(context.current_dt.time()))
    send_message('美好的一天~')
    g.security = "000567.XSHE"

def market_open(context):
    log.info('函数运行时间(market_open):'+str(context.current_dt.time()))
    security = g.security
    close_data = get_bars(security, count=5, unit='1d', fields=['close'])

    # 取得上一时间点价格
    current_price = close_data['close'][-1]
    # 取得当前的现金
    cash = context.portfolio.available_cash
    MA5 = close_data['close'].mean()

    # 判断是否满仓
    if cash < current_price*100:
        full_position = True
    else:
        full_position = False

    # 判断是否空仓
    if context.portfolio.long_positions == {}:
        empty_position = True
    else:
        empty_position = False

    if full_position == True and len(context.portfolio.positions) > 0:
        for stock in context.portfolio.positions.keys():
            W5 = get_bars(stock, count=5, unit='1w', fields=['close'])['close'].mean()
            stock_current_price = context.portfolio.positions[stock].price
            stock_total_account = context.portfolio.positions[stock].total_amount
            if stock_current_price > W5*1.09 or stock_current_price < W5*0.97:
                order_target(stock, stock_total_account/2)
                log.info("价格低于在5周均价3或者高于9%, 卖出半仓 %s" % (security))

    if empty_position == False and full_position == False:
        security_W5 = get_bars(security, count=5, unit='1w', fields=['close'])['close'].mean()
        if current_price < security_W5+0.05 and current_price > security_W5-0.05:
            order_value(security, cash)
            log.info("半仓情况，价格在5周均价上下浮动0.05元, 买入全仓 %s" % (security))

    if current_price < (MA5+0.05) and current_price > (MA5-0.05) and empty_position == True:
        order_value(security, (cash/2))
        log.info("空仓情况，价格在5日均价上下浮动0.05元, 建仓，半仓 %s" % (security))
        
    if len(context.portfolio.positions) > 0:
        for stock in context.portfolio.positions.keys():
            W5 = get_bars(stock, count=5, unit='1w', fields=['close'])['close'].mean()
            stock_current_price = context.portfolio.positions[stock].price
            if stock_current_price < W5*0.98:
                order_target(stock, 0)
                log.info("价格低于5周均价, 清仓 %s" % (security))
            
