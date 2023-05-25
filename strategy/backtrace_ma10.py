import talib as tl  # 引入 talib 库，用于计算均线
import pandas as pd  # 引入 pandas 库，用于数据处理
import logging  # 引入 logging 库，用于日志记录
from datetime import datetime, timedelta  # 引入 datetime 库，用于日期计算

def check(code_name, data, end_date=None, threshold=20):
    """
    回踩 10 日线策略
    :param code_name: 股票代码和名称
    :param data: 股票历史数据，包含日期、开盘价、收盘价、最高价、最低价、成交量、涨跌幅等信息
    :param end_date: 回测结束日期
    :param threshold: 回测天数
    :return: 是否符合回踩 10 日线策略
    """
    if len(data) < 20:
        logging.debug(f"{code_name}:样本小于 20 天...\n")  # 记录日志，样本小于 20 天
        return False

    # 计算 10 日线和 20 日线
    data['ma10'] = pd.Series(tl.MA(data['收盘'].values, 10), index=data.index.values)  # 计算 10 日均线
    data['ma20'] = pd.Series(tl.MA(data['收盘'].values, 20), index=data.index.values)  # 计算 20 日均线

    begin_date = data.iloc[0].日期  # 获取数据的开始日期
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug(f"{code_name}在{end_date}时还未上市")  # 记录日志，该股票在回测结束日期时还未上市
            return False
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]  # 截取回测结束日期之前的数据
    data = data.tail(n=threshold)  # 截取最近 threshold 天的数据

    # 计算区间最高、最低价格和是否存在涨停
    lowest_row = data.iloc[-1]  # 获取最近 threshold 天的最低价
    highest_row = data.iloc[-1]  # 获取最近 threshold 天的最高价
    recent_lowest_row = data.iloc[-1]  # 获取最近 threshold 天的最低价
    hang_up_exists = False  # 是否存在涨停
    for index, row in data.iterrows():
        if row['涨跌幅'] > 9.8:
            hang_up_exists = True  # 存在涨停
        if row['收盘'] > highest_row['收盘']:
            highest_row = row  # 获取最近 threshold 天的最高价
        elif row['收盘'] < lowest_row['收盘']:
            lowest_row = row  # 获取最近 threshold 天的最低价

    if (lowest_row['成交量'] == 0) or (highest_row['成交量'] == 0) or (not hang_up_exists):
        return False  # 如果最低价或最高价的成交量为 0，或不存在涨停，则不符合回踩 10 日线策略

    # 分割前后两个区间
    data_front = data.loc[(data['日期'] < highest_row['日期'])]  # 获取最高价之前的数据
    data_end = data.loc[(data['日期'] >= highest_row['日期'])]  # 获取最高价之后的数据
    if data_front.empty or data_end.empty:
        return False  # 如果前后两个区间中有一个为空，则不符合回踩 10 日线策略

    # 前半段由 10 日线以下向上突破
    if not (data_front.iloc[0]['收盘'] < data_front.iloc[0]['ma10'] or
            data_front.iloc[-1]['收盘'] < data_front.iloc[-1]['ma10']):
        return False  # 如果前半段不是由 10 日线以下向上突破，则不符合回踩 10 日线策略

    # 后半段在 10 日线以上运行（回踩 10 日线）
    for index, row in data_end.iterrows():
        if row['收盘'] < row['ma10']:
            return False  # 如果后半段不在 10 日线以上运行，则不符合回踩 10 日线策略
        if row['收盘'] < recent_lowest_row['收盘']:
            recent_lowest_row = row  # 获取最近 threshold 天的最低价

    # 近2天最低
    lowest_date_diff = datetime.date(datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d')) - \
                       datetime.date(datetime.strptime(data.iloc[-1]['日期'], '%Y-%m-%d'))
    if not (timedelta(days=0) <= lowest_date_diff <= timedelta(days=1)):
        return False  # 如果最近 threshold 天的最低价不是在最近 2 天内，则不符合回踩 10 日线策略

    # 近期回调 3-5 天
    back_date_diff = datetime.date(datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d')) - \
                     datetime.date(datetime.strptime(highest_row['日期'], '%Y-%m-%d'))
    if not (timedelta(days=3) <= back_date_diff <= timedelta(days=10)):
        return False  # 如果最近 threshold 天的最低价不是在最近 3-5 天内，则不符合回踩 10 日线策略

    # 回踩且缩量
    back_ratio = (highest_row['收盘'] - recent_lowest_row['收盘']) / highest_row['收盘']
    vol_ratio = highest_row['成交量'] / recent_lowest_row['成交量']
    if back_ratio < 0.03 or vol_ratio < 2:
        return False  # 如果回踩幅度小于 3% 或成交量比例小于 2，则不符合回踩 10 日线策略

    # 收盘涨跌幅小于1%且收盘价较低点上涨幅度小于2%
    up_down_range = data.iloc[-1]['涨跌幅']
    increase_ratio = (recent_lowest_row['收盘'] - data.iloc[-1]['收盘']) / recent_lowest_row['收盘']
    if up_down_range >= 1 or increase_ratio >= 0.02:
        return False  # 如果收盘涨跌幅大于等于 1% 或收盘价较低点上涨幅度大于等于 2%，则不符合回踩 10 日线策略

    return True  # 符合回踩 10 日
