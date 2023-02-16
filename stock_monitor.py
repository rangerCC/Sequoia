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

def prepare():
    if not settings.config['monitor']['enable'] :
        return

    # 实时行情信息
    all_data = ak.stock_zh_a_spot_em()

    stocks = settings.config['monitor']['stocks']
    if len(stocks) == 0 :
        return
    
    for stock in stocks :
        process(stock,all_data)


def process(stock,all_data):
    code = stock['code']
    up = stock['up']
    down = stock['down']
    stock_data = all_data.loc[(all_data['代码'] == code)].iloc[0]
    current_price = stock_data['最新价']
    if up > 0 and current_price >= up :
        msg = "【个股追踪提醒】\n"
        msg = msg + '\n{} {}\n\n当前股价【{}】\n\n已上涨至预设定价格【{}】\n'.format(stock_data['代码'], stock_data['名称'], stock_data['最新价'], up)
        push.statistics(msg)

    if down > 0 and current_price <= down :
        msg = "【个股追踪提醒】\n"
        msg = '\n{} {}\n当前股价【{}】\n已下跌至预设定价格【{}】\n'.format(stock_data['代码'], stock_data['名称'], stock_data['最新价'], down)
        push.statistics(msg)

    # 个股信息
    # stock_individual_info_em_df = ak.stock_individual_info_em(symbol=code)
    
    
