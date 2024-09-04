# -*- encoding: UTF-8 -*-
import data_fetcher
import settings
import utils
import akshare as ak
from wxpusher import WxPusher
import push
import logging
import time
from datetime import datetime, timedelta
import pandas as pd

def prepare():
    if not settings.config['monitor']['enable'] :
        return

    stocks = settings.config['monitor']['stocks']
    if len(stocks) == 0 :
        return

    # 股东户数
    # gdhs_data = ak.stock_zh_a_gdhs_detail_em(symbol="002168")

    # 区间基本统计
    for stock in stocks :
        process_statistics(stock)

    # 日内分时数据
    # rnfs_data = ak.stock_intraday_sina(symbol="sz002168", date="20240904")

    # 实时行情信息
    for stock in stocks :
        process_monitor(stock)

def process_statistics(stock):
    if stock['code'] is None:
        return
    code = stock['code']
    today = datetime.today().strftime("%Y%m%d")
    t_360_days_ago = (datetime.now() - timedelta(days=360)).strftime("%Y%m%d")

    data = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=t_360_days_ago, adjust="qfq")
    subset = data[['日期' ,'股票代码', '收盘', '成交量', '涨跌幅', '换手率']]
    subset_map = [tuple(x) for x in subset.values]
    df = pd.DataFrame(subset_map, columns=['日期' ,'股票代码', '收盘', '成交量', '涨跌幅', '换手率'])
    df.to_excel('output.xlsx', index=False)

def process_monitor(stock):
    if stock['code'] is None:
        return
    code = stock['code']
    up = stock['up']
    down = stock['down']
    data = ak.stock_zh_a_spot_em()
    stock_data = data.loc[(data['代码'] == code)].iloc[0]
    current_price = stock_data['最新价']

    # 基本信息
    msg = "【个股追踪提醒】\n"
    msg = msg + '\n{} {}\n\n当前股价：【{}】\n\n换手率：【{}】\n\n成交量：【{}】\n\n涨跌幅：【{}】'.format(stock_data['代码'], stock_data['名称'], stock_data['最新价'], stock_data['换手率'], stock_data['成交量'], stock_data['涨跌幅'])
    push.statistics(msg)

    # 价格上限处理
    if up > 0 and current_price >= up :
        msg = "【个股追踪提醒】\n"
        msg = msg + '\n{} {}\n\n当前股价【{}】\n\n已上涨至预设定价格【{}】\n'.format(stock_data['代码'], stock_data['名称'], stock_data['最新价'], up)
        push.statistics(msg)

    # 价格下限处理
    if down > 0 and current_price <= down :
        msg = "【个股追踪提醒】\n"
        msg = msg + '\n{} {}\n当前股价【{}】\n已下跌至预设定价格【{}】\n'.format(stock_data['代码'], stock_data['名称'], stock_data['最新价'], down)
        push.statistics(msg)

    # 个股信息
    # stock_individual_info_em_df = ak.stock_individual_info_em(symbol=code)
    
    
