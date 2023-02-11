# -*- encoding: UTF-8 -*-

import data_fetcher
import settings
import utils
import strategy.enter as enter
from strategy import turtle_trade, climax_limitdown
from strategy import backtrace_ma10
from strategy import backtrace_ma20
from strategy import backtrace_ma55
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_backtrace_increase
from strategy import keep_increasing
from strategy import high_tight_flag
from strategy import turtle_trade_limitup
import akshare as ak
import push
import logging
import time
import datetime


def prepare():
    logging.info("\n************************ process start ***************************************\n\n")
    all_data = ak.stock_zh_a_spot_em() # 实时行情

    stock_market_activity = ak.stock_market_activity_legu()
    statistics(stock_market_activity)
    
    subset = all_data[['代码', '名称', '涨跌幅']]
    stocks = [tuple(x) for x in subset.values]
    stocks = filter_stocks(stocks) # 过滤科创，300，ST，N

    strategies = {
        '亮哥的停机坪': parking_apron.check,
        '亮哥的大海龟': turtle_trade_limitup.check_enter,
        # '今日高而窄旗形': high_tight_flag.check,
        # '今日托底回踩55日均线': backtrace_ma55.check,
        # '今日回踩年线': backtrace_ma250.check,
        # '今日均线多头': keep_increasing.check,
        # '放量上涨': enter.check_volume,
        # '突破平台': breakthrough_platform.check,
        # '无大幅回撤': low_backtrace_increase.check,
        # '放量跌停': climax_limitdown.check,
        # '低吸停机坪': parking_apron.check,
        '低吸长线牛': backtrace_ma250.check,
        '低吸波段牛': backtrace_ma55.check,
        '低吸短线牛': backtrace_ma20.check,
        '低吸超短牛': backtrace_ma10.check,
        '近期突破牛': backtrace_ma10.check,
    }

    process(stocks, strategies)

    logging.info("\n************************ process   end ***************************************\n")

def process(stocks, strategies):
    stocks_data = data_fetcher.run(stocks)
    for strategy, strategy_func in strategies.items():
        check(stocks_data, strategy, strategy_func)
        time.sleep(2)

def check(stocks_data, strategy, strategy_func):
    end = settings.config['end_date']
    m_filter = check_enter(end_date=end, strategy_fun=strategy_func)
    results = dict(filter(m_filter, stocks_data.items()))
    if len(results) > 0:
        push.strategy('**************"{0}"**************\n\n{1}\n\n**************"{0}"**************\n'.format(strategy, list(results.keys())))


def check_enter(end_date=None, strategy_fun=enter.check_volume):
    def end_date_filter(stock_data):
        if end_date is not None:
            if end_date < stock_data[1].iloc[0].日期:  # 该股票在end_date时还未上市
                logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                return False
        return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)


    return end_date_filter


# 统计数据
def statistics(stock_market_activity):
    msg = "【今日A股数据概览】\n"
    for index, row in stock_market_activity.iterrows() :
        if row[0] == '活跃度' or row[0] == '统计日期':
            msg = msg + "{}：{}\n".format(row[0],row[1])
        else :
            msg = msg + "{}：{}\n".format(row[0],int(row[1]))
    push.statistics(msg)

# 过滤指定股票
def filter_stocks(stock_list):
    return [stock for stock in stock_list if not (
        stock[0].startswith('68') or
        stock[0].startswith('83') or
        stock[0].startswith('30') or
        'ST' in stock[1] or
        '*'  in stock[1] or
        '退' in stock[1] or
        'N' in stock[1])]
