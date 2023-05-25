# -*- encoding: UTF-8 -*-
import settings
import akshare as ak
from wxpusher import WxPusher
import push
from datetime import datetime, timedelta

def prepare():
    # 如果监控功能未开启，则直接返回
    if not settings.config['monitor']['enable']:
        return

    # 获取实时行情信息
    all_data = ak.stock_zh_a_spot_em()

    # 获取需要监控的股票列表
    stocks = settings.config['monitor']['stocks']
    if not stocks:
        return

    # 遍历股票列表，处理每一支股票
    for stock in stocks:
        process(stock, all_data)


def process(stock, all_data):
    # 获取股票代码、上涨预警价格、下跌预警价格
    code = stock['code']
    up = stock['up']
    down = stock['down']

    # 获取股票实时数据
    stock_data = all_data.loc[all_data['代码'] == code].iloc[0]
    current_price = stock_data['最新价']

    # 如果上涨预警价格大于0且当前价格大于等于上涨预警价格，则发送上涨提醒消息
    if up > 0 and current_price >= up:
        msg = f"【个股追踪提醒】\n\n{stock_data['代码']} {stock_data['名称']}\n\n当前股价【{stock_data['最新价']}】\n\n已上涨至预设定价格【{up}】\n"
        push.statistics(msg)

    # 如果下跌预警价格大于0且当前价格小于等于下跌预警价格，则发送下跌提醒消息
    if down > 0 and current_price <= down:
        msg = f"【个股追踪提醒】\n\n{stock_data['代码']} {stock_data['名称']}\n\n当前股价【{stock_data['最新价']}】\n\n已下跌至预设定价格【{down}】\n"
        push.statistics(msg)

    # 获取个股信息
    # stock_individual_info_em_df = ak.stock_individual_info_em(symbol=code)
