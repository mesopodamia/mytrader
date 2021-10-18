# 导入聚宽函数库
import jqdata

def initialize(context):
    g.security = '000001.XSHE'
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)

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

    if MA60 > MA20 and MA10 > MA30:
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
