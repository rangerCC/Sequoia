import talib as tl
import pandas as pd
import logging
from datetime import datetime, timedelta


def check(code_name, data, end_date=None, threshold=60):
    # 样本小于60天
    if len(data) < 60:
        logging.debug(f"{code_name}: 样本小于60天...\n")
        return

    # 计算MA10、MA20、MA55
    data['ma10'] = tl.MA(data['收盘'].values, 10)
    data['ma20'] = tl.MA(data['收盘'].values, 20)
    data['ma55'] = tl.MA(data['收盘'].values, 55)

    # 筛选数据
    begin_date = data.iloc[0].日期
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug(f"{code_name}在{end_date}时还未上市")
            return False
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold)

    # 获取最后收盘价、开盘价
    last_close = data.iloc[-1]['收盘']
    last_open = data.iloc[-1]['开盘']

    # 获取区间最低点、最高点、近期低点
    lowest_row = data.iloc[-1]
    highest_row = data.iloc[-1]
    recent_lowest_row = data.iloc[-1]
    for index, row in data.iterrows():
        if row['收盘'] > highest_row['收盘']:
            highest_row = row
        elif row['收盘'] < lowest_row['收盘']:
            lowest_row = row

    # 成交量为0，忽略
    if lowest_row['成交量'] == 0 or highest_row['成交量'] == 0:
        return False

    # 获取前半段、后半段数据
    data_front = data.loc[(data['日期'] < highest_row['日期'])]
    data_end = data.loc[(data['日期'] >= highest_row['日期'])]

    # 下行趋势，则忽略
    if data_front.empty:
        return False

    # 前半段由55日线下向上突破
    if not (data_front.iloc[0]['收盘'] < data_front.iloc[0]['ma55'] and
            data_front.iloc[-1]['收盘'] > data_front.iloc[-1]['ma55']):
        return False

    # 后半段必须在55日线上运行
    for index, row in data_end.iterrows():
        if row['收盘'] < row['ma55']:
            return False
        if row['收盘'] < recent_lowest_row['收盘']:
            recent_lowest_row = row

    # 计算日期差
    date_diff = datetime.date(datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d')) - \
                datetime.date(datetime.strptime(highest_row['日期'], '%Y-%m-%d'))

    # 日期差不在10~50天之间，忽略
    if not (timedelta(days=10) <= date_diff <= timedelta(days=50)):
        return False

    # 回踩伴随缩量
    vol_ratio = highest_row['成交量'] / recent_lowest_row['成交量']
    back_ratio = recent_lowest_row['收盘'] / highest_row['收盘']
    if not (vol_ratio > 2 and back_ratio < 0.8 and last_close < last_open):
        return False

    # MA10与MA20交叉
    data_cross = data_front.loc[-0.01 <= (data_front.ma10 - data_front.ma20) <= 0.01]
    if not (len(data_cross) > 1):
        return False

    # 昨日收盘价较交叉点上涨幅度小于3%
    increase_ratio = (last_close - data_cross.iloc[-1]['收盘']) / data_cross.iloc[-1]['收盘']
    if not increase_ratio < 0.03:
        return False

    return True
