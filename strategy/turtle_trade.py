# -*- coding: UTF-8 -*-

# 总市值
BALANCE = 200000


def check_enter(code_name, data, end_date=None, threshold=60):
    """
    检查是否满足条件，最后一个交易日收市价为指定区间内最高价
    :param code_name: 股票代码
    :param data: 股票数据
    :param end_date: 截止日期
    :param threshold: 区间长度
    :return: 是否满足条件
    """
    # 如果有截止日期，只保留截止日期之前的数据
    if end_date is not None:
        data = data[data['日期'] <= end_date]
    # 如果数据为空或者数据长度小于指定区间长度，不满足条件
    if data is None or len(data) < threshold:
        return False

    # 取出最后指定区间长度的数据
    tail_data = data.tail(n=threshold)
    # 取出最高价
    max_price = tail_data['收盘'].max()
    # 取出最后一个交易日的收盘价
    last_close = tail_data.iloc[-1]['收盘']

    # 如果最后一个交易日的收盘价大于等于最高价，满足条件
    return last_close >= max_price
