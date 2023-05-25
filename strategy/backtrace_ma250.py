import talib as tl  # 导入 talib 库，用于计算技术指标
import pandas as pd  # 导入 pandas 库，用于数据处理
import logging  # 导入 logging 库，用于输出日志信息
from datetime import datetime, timedelta  # 导入 datetime 库，用于处理日期时间

def check(code_name, data, end_date=None, threshold=120):
    """
    检查股票是否符合条件

    :param code_name: str 股票代码
    :param data: pd.DataFrame 股票数据
    :param end_date: str 截止日期，默认为 None
    :param threshold: int 样本数量，默认为 120
    :return: bool 是否符合条件
    """
    if len(data) < 120:
        logging.debug(f"{code_name}: 样本小于 120 天...\n")
        return

    data['ma10'] = tl.MA(data['收盘'].values, 10)  # 计算10日均线
    data['ma20'] = tl.MA(data['收盘'].values, 20)  # 计算20日均线
    data['ma55'] = tl.MA(data['收盘'].values, 55)  # 计算55日均线
    data['ma250'] = tl.MA(data['收盘'].values, 250)  # 计算250日均线

    begin_date = data.iloc[0].日期  # 获取数据的开始日期
    if end_date is not None and end_date < begin_date:
        logging.debug(f"{code_name}在{end_date}时还未上市")  # 输出日志信息
        return False

    data = data.loc[data['日期'] <= end_date] if end_date else data  # 如果有截止日期，截取数据
    data = data.tail(n=threshold)  # 截取最近 threshold 天的数据

    lowest_row = data.iloc[-1]  # 获取最近一天的数据
    highest_row = data.iloc[-1]  # 获取最近一天的数据
    recent_lowest_row = data.iloc[-1]  # 获取最近一天的数据

    hang_up_exists = False  # 是否存在涨停
    for index, row in data.iterrows():
        if row['涨跌幅'] > 9.8:
            hang_up_exists = True  # 存在涨停
        if row['收盘'] > highest_row['收盘']:
            highest_row = row  # 获取最高价的数据
        elif row['收盘'] < lowest_row['收盘']:
            lowest_row = row  # 获取最低价的数据

    if lowest_row['成交量'] == 0 or highest_row['成交量'] == 0 or not hang_up_exists:
        return False  # 如果最低价或最高价的成交量为0或不存在涨停，则不符合条件

    data_front = data.loc[data['日期'] < highest_row['日期']]
    data_end = data.loc[data['日期'] >= highest_row['日期']]
    if data_front.empty or data_end.empty:
        return False  # 如果数据为空，则不符合条件

    if not (data_front.iloc[0]['收盘'] < data_front.iloc[0]['ma250'] or
            data_front.iloc[-1]['收盘'] < data_front.iloc[-1]['ma250']):
        return False  # 如果前面的数据不在250日均线下或后面的数据不在250日均线下，则不符合条件

    for index, row in data_end.iterrows():
        if row['收盘'] < row['ma250']:
            return False  # 如果后面的数据不在250日均线下，则不符合条件
        if row['收盘'] < recent_lowest_row['收盘']:
            recent_lowest_row = row  # 获取最近的最低价数据

    back_date_diff = datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d') - \
                     datetime.strptime(highest_row['日期'], '%Y-%m-%d')
    if not (timedelta(days=30) <= back_date_diff <= timedelta(days=100)):
        return False  # 如果最近的最低价数据和最高价数据之间的时间差不在30到100天之间，则不符合条件

    back_ratio = (highest_row['收盘'] - recent_lowest_row['收盘']) / highest_row['收盘']  # 计算回撤比例
    vol_ratio = highest_row['成交量'] / recent_lowest_row['成交量']  # 计算成交量比例
    if back_ratio < 0.03 or vol_ratio < 2:
        return False  # 如果回撤比例小于0.03或成交量比例小于2，则不符合条件

    up_down_range = data.iloc[-1]['涨跌幅']  # 获取最近一天的涨跌幅
    increase_ratio = (recent_lowest_row['收盘'] - data.iloc[-1]['收盘']) / recent_lowest_row['收盘']  # 计算涨幅比例
    if up_down_range >= 1 or increase_ratio >= 0.02:
        return False  # 如果最近一天的涨跌幅大于等于1或涨幅比例大于等于0.02，则不符合条件

    return True  # 符合
