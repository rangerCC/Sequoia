import talib as tl
import pandas as pd
import logging


def check(code_name, data, end_date=None, threshold=30):
    """
    检查股票是否持续上涨（MA30向上）
    :param code_name: 股票代码
    :param data: 股票历史数据
    :param end_date: 截止日期
    :param threshold: 样本天数
    :return: True or False
    """
    if len(data) < threshold:
        # 样本天数小于阈值
        logging.debug(f"{code_name}: 样本小于{threshold}天...\n")
        return False

    # 计算MA30
    data['ma30'] = tl.MA(data['收盘'].values, 30)

    # 截取数据
    if end_date is not None:
        # 截止日期之前的数据
        mask = data['日期'] <= end_date
        data = data.loc[mask]

    # 取最近的 threshold 天数据
    data = data.tail(n=threshold)

    # 判断MA30是否持续上涨
    ma30 = data['ma30']
    if ma30.iloc[0] < ma30.iloc[threshold//3] < ma30.iloc[threshold*2//3] < ma30.iloc[-1] and \
            ma30.iloc[-1] > 1.2 * ma30.iloc[0]:
        # MA30 持续上涨
        return True
    else:
        # MA30 没有持续上涨
        return False
