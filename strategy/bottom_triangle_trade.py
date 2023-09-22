# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging
from datetime import datetime, timedelta

# 使用示例：result = backtrace_ma55.check(code_name, data, end_date=end_date)
# 如：当end_date='2019-02-01'，输出选股结果如下：
# [('601616', '广电电气'), ('002243', '通产丽星'), ('000070', '特发信息'), ('300632', '光莆股份'), ('601700', '风范股份'), ('002017', '东信和平'), ('600775', '南京熊猫'), ('300265', '通光线缆'), ('600677', '航天通信'), ('600776', '东方通信')]
# 当然，该函数中的参数可能存在过拟合的问题


# 底部托底三角策略
def check(code_name, data, end_date=None, threshold=60):
    if len(data) < 60:
        logging.debug("{0}:样本小于60天...\n".format(code_name))
        return
    
    data['ma10'] = pd.Series(tl.MA(data['收盘'].values, 10), index=data.index.values)
    data['ma20'] = pd.Series(tl.MA(data['收盘'].values, 20), index=data.index.values)
    data['ma55'] = pd.Series(tl.MA(data['收盘'].values, 55), index=data.index.values)

    begin_date = data.iloc[0].日期
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug("{}在{}时还未上市".format(code_name, end_date))
            return False
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    data = data.tail(n=threshold)

    # 最后收盘、开盘价
    last_close = data.iloc[-1]['收盘']
    last_open =  data.iloc[-1]['开盘']

    # 区间最低点
    lowest_row = data.iloc[-1]
    # 区间最高点
    highest_row = data.iloc[-1]

    # 近期低点
    recent_lowest_row = data.iloc[-1]

    # 计算区间最高、最低价格
    for index, row in data.iterrows():
        if row['收盘'] > highest_row['收盘']:
            highest_row = row
        elif row['收盘'] < lowest_row['收盘']:
            lowest_row = row

    if lowest_row['成交量'] == 0 or highest_row['成交量'] == 0:
        return False

    data_front = data.loc[(data['日期'] < highest_row['日期'])]
    data_end = data.loc[(data['日期'] >= highest_row['日期'])]

    # 下行趋势，则忽略
    if data_front.empty:
        return False
    
    # 前半段由55日线下向上突破
    if not (data_front.iloc[0]['收盘'] < data_front.iloc[0]['ma55'] and
            data_front.iloc[-1]['收盘'] > data_front.iloc[-1]['ma55']):
        return False

    if not data_end.empty:
        # 后半段必须在55日线上运行
        for index, row in data_end.iterrows():
            if row['收盘'] < row['ma55']:
                return False
            if row['收盘'] < recent_lowest_row['收盘']:
                recent_lowest_row = row

    date_diff = datetime.date(datetime.strptime(recent_lowest_row['日期'].isoformat(), '%Y-%m-%d')) - \
                datetime.date(datetime.strptime(highest_row['日期'].isoformat(), '%Y-%m-%d'))

    if not(timedelta(days=10) <= date_diff <= timedelta(days=50)):
        return False
    
    # 回踩伴随缩量
    vol_ratio = highest_row['成交量']/recent_lowest_row['成交量']
    back_ratio = recent_lowest_row['收盘'] / highest_row['收盘']

    if not (vol_ratio > 2 and back_ratio < 0.8 and last_close < last_open) :
        return False
    
    if data_front.ma20.empty :
        return False
    
    data_cross = data_front.loc[-0.01 <= (data_front.ma10-data_front.ma20) <= 0.01]
    if not (len(data_cross) > 1):
        return False

    # 昨日收盘价较交叉点上涨幅度小于3%
    increase_ratio = (last_close - data_cross.iloc[-1]['收盘']) / data_cross.iloc[-1]['收盘']
    if not increase_ratio < 0.03 :
        return False

    return True

