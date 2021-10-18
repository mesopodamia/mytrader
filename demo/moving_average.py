# 导入聚宽函数库
import jqdata

def initialize(context):
    g.security = '000001.XSHE'
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)

# 获取000001.XSHE当前交易日date_nowadays的前一个交易日的5日的MA的数值，那么传入参数为('000001.XSHE', context.current_dt.date(), 1, 5)  
def get_MA(code, date_nowadays, n_date, days):
   trade_dates_list = get_trade_days(end_date=date_nowadays, count=n_date+1)
   date_that_get_MA = trade_dates_list[-n_date-1]
   price_data = get_price(code, start_date=None, end_date=date_that_get_MA, frequency='daily', fields=None, skip_paused=False, fq='pre', count=days, panel=True)
   MA = price_data['close'].mean()
   return MA

def handle_data(context, data):
    security = g.security
    # 获取股票的收盘价
    close_data = attribute_history(security, 5, '1d', ['close'])
    MA5 = close_data['close'].mean()
    MA60 = attribute_history(security, 60, '1d', ['close'])['close'].mean()
    MA30 = attribute_history(security, 30, '1d', ['close'])['close'].mean()
    MA20 = attribute_history(security, 20, '1d', ['close'])['close'].mean()
    MA10 = attribute_history(security, 10, '1d', ['close'])['close'].mean()

    cash = context.portfolio.available_cash

    count = 0
    for x in range(10):
        n = 1 + x
        C_MA60 = get_MA(security, context.current_dt.date(), n, 60)
        C_MA10 = get_MA(security, context.current_dt.date(), n, 10)
        if C_MA60 > C_MA10:
            count = count + 1
    if count == 10 or MA60 > MA20:
        if context.current_dt.strftime('%H:%M:%S') > '14:30:00' and MA10 > MA30:        
            order_value(security, cash)
            log.info("买入开仓 %s" % (security))

    if len(context.portfolio.positions) > 0:
        for stock in context.portfolio.positions.keys():
            df = get_price(stock, start_date=context.portfolio.positions[stock].init_time,\
                end_date=context.previous_date, frequency='minute', fields=['high'], skip_paused=True)
            df_max_high = df["high"].max()  #从买入至今的最高价
            current_price = context.portfolio.positions[stock].price # 当前价格

            if 1-current_price/df_max_high >= 0.25: # 最高价回撤25%，止损
                order_target_value(stock, 0)
                log.info("最高价回撤25%，止损 %s" % (security))
                continue

            if current_price / context.portfolio.positions[stock].avg_cost < 0.8: # 亏损20%，止损
                log.info("亏损20%，止损 %s" % (security))
                order_target(stock, 0)
            
            if MA10 < MA30 or MA60 < MA20: #均价变动，止损
                order_target(stock, 0)
                log.info("均价变动，止损 %s" % (security))
