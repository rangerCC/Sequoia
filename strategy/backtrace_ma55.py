# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging
from datetime import datetime, timedelta


def check(code_name, data, end_date=None, threshold=60):
    """
    回踩10日线策略
    :param code_name: 股票代码和名称
    :param data: 股票数据
    :param end_date: 回测结束日期
    :param threshold: 回测天数
    :return: 是否符合回踩10日线策略
    """
    # 如果数据样本小于threshold，返回False
    if len(data) < threshold:
        logging.debug(f"{code_name}: 样本小于{threshold}天...\n")
        return False

    # 计算10日线、20日线和55日线
    data['ma10'] = pd.Series(tl.MA(data['收盘'].values, 10), index=data.index.values)
    data['ma20'] = pd.Series(tl.MA(data['收盘'].values, 20), index=data.index.values)
    data['ma55'] = pd.Series(tl.MA(data['收盘'].values, 55), index=data.index.values)

    begin_date = data.iloc[0].日期
    if end_date is not None:
        # 如果股票在end_date时还未上市，返回False
        if end_date < begin_date:
            logging.debug(f"{code_name}在{end_date}时还未上市")
            return False
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold)

    # 区间最低点
    lowest_row = data.iloc[-1]
    # 区间最高点
    highest_row = data.iloc[-1]
    # 近期低点
    recent_lowest_row = data.iloc[-1]

    # 计算区间最高、最低价格
    hang_up_exists = False
    for _, row in data.iterrows():
        # 如果存在涨停，将hang_up_exists设置为True
        if row['涨跌幅'] > 9.8:
            hang_up_exists = True
        if row['收盘'] > highest_row['收盘']:
            highest_row = row
        elif row['收盘'] < lowest_row['收盘']:
            lowest_row = row

    # 如果区间最高点和区间最低点的成交量为0或者不存在涨停，返回False
    if (lowest_row['成交量'] == 0) or (highest_row['成交量'] == 0) or (not hang_up_exists):
        return False

    # 将数据分为前半段和后半段
    data_front = data.loc[(data['日期'] < highest_row['日期'])]
    data_end = data.loc[(data['日期'] >= highest_row['日期'])]
    if data_front.empty or data_end.empty:
        return False

    # 前半段由 55 日线以下向上突破
    if not (data_front.iloc[0]['收盘'] < data_front.iloc[0]['ma55'] or
            data_front.iloc[-1]['收盘'] < data_front.iloc[-1]['ma55']):
        return False

    # 后半段在 55 日线以上运行（回踩 55 日线）
    for _, row in data_end.iterrows():
        if row['收盘'] < row['ma55']:
            return False
        if row['收盘'] < recent_lowest_row['收盘']:
            recent_lowest_row = row

    # 近2天最低
    lowest_date_diff = datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d') - \
                       datetime.strptime(data.iloc[-1]['日期'], '%Y-%m-%d')
    # 如果近2天最低点不在最后一天或者前一天，返回False
    if not (timedelta(days=0) <= lowest_date_diff <= timedelta(days=1)):
        return False

    # 近期回调 10-50 天
    back_date_diff = datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d') - \
                     datetime.strptime(highest_row['日期'], '%Y-%m-%d')
    # 如果回调天数不在10-50天之间，返回False
    if not (timedelta(days=10) <= back_date_diff <= timedelta(days=50)):
        return False

    # 回踩且缩量
    back_ratio = (highest_row['收盘'] - recent_lowest_row['收盘']) / highest_row['收盘']
    vol_ratio = highest_row['成交量'] / recent_lowest_row['成交量']
    # 如果回踩幅度小于3%或者成交量比例小于2，返回False
    if back_ratio < 0.03 or vol_ratio < 2:
        return False

    # 收盘涨跌幅小于1%且收盘价较低点上涨幅度小于2%
    up_down_range = data.iloc[-1]['涨跌幅']
    increase_ratio = (recent_lowest_row['收盘'] - data.iloc[-1]['收盘']) / recent_lowest_row['收盘']
    # 如果收盘涨跌幅大于等于1%或者收盘价较低点上涨幅度大于等于2%，返回False
    if up_down_range >= 1 or increase_ratio >= 0.02:
        return False

    return True
