# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging
from datetime import datetime, timedelta


# 回踩10日线策略
def check(code_name, data, end_date=None, threshold=40):
    if len(data) < 40:
        logging.debug(f"{code_name}: 样本小于 40 天...\n")
        return
    
    data['ma10'] = pd.Series(tl.MA(data['收盘'].values, 10), index=data.index.values)
    data['ma20'] = pd.Series(tl.MA(data['收盘'].values, 20), index=data.index.values)
    data['ma55'] = pd.Series(tl.MA(data['收盘'].values, 55), index=data.index.values)

    begin_date = data.iloc[0].日期
    if end_date is not None and end_date < begin_date:
        logging.debug(f"{code_name}在{end_date}时还未上市")
        return False

    data = data.tail(n=threshold)

    # 区间最低点
    lowest_row = data.iloc[-1]
    # 区间最高点
    highest_row = data.iloc[-1]
    # 近期低点
    recent_lowest_row = data.iloc[-1]

    # 计算区间最高、最低价格
    hang_up_exists = False
    for index, row in data.iterrows():
        if row['涨跌幅'] > 9.8:
            hang_up_exists = True
        if row['收盘'] > highest_row['收盘']:
            highest_row = row
        elif row['收盘'] < lowest_row['收盘']:
            lowest_row = row

    if lowest_row['成交量'] == 0 or highest_row['成交量'] == 0 or not hang_up_exists:
        return False

    data_front = data.loc[(data['日期'] < highest_row['日期'])]
    data_end = data.loc[(data['日期'] >= highest_row['日期'])]
    if data_front.empty or data_end.empty :
        return False
    
    # 前半段由 20 日线以下向上突破
    if not (data_front.iloc[0]['收盘'] < data_front.iloc[0]['ma20'] or
            data_front.iloc[-1]['收盘'] < data_front.iloc[-1]['ma20']):
        return False

    # 后半段在 20 日线以上运行（回踩 20 日线）
    for index, row in data_end.iterrows():
        if row['收盘'] < row['ma20']:
            return False
        if row['收盘'] < recent_lowest_row['收盘']:
            recent_lowest_row = row

    # 近2天最低
    lowest_date_diff = datetime.date(datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d')) - \
                datetime.date(datetime.strptime(data.iloc[-1]['日期'], '%Y-%m-%d'))
    if not (timedelta(days=0) <= lowest_date_diff <= timedelta(days=1)):
        return False
    
    # 近期回调 5-20 天
    back_date_diff = datetime.date(datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d')) - \
                datetime.date(datetime.strptime(highest_row['日期'], '%Y-%m-%d'))
    if not (timedelta(days=5) <= back_date_diff <= timedelta(days=20)):
        return False
    
    # 回踩且缩量
    back_ratio = (highest_row['收盘'] - recent_lowest_row['收盘']) / highest_row['收盘']
    vol_ratio = highest_row['成交量'] / recent_lowest_row['成交量']
    if back_ratio < 0.03 or vol_ratio < 2:
        return False

    # 收盘涨跌幅小于1%且收盘价较低点上涨幅度小于2%
    up_down_range = data.iloc[-1]['涨跌幅']
    increase_ratio = (recent_lowest_row['收盘'] - data.iloc[-1]['收盘']) / recent_lowest_row['收盘']
    if up_down_range >= 1 or increase_ratio >= 0.02:
        return False

    return True
