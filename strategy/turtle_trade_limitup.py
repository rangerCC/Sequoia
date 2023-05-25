# -*- coding: UTF-8 -*-

import logging

def check(code_name, data, end_date=None, threshold=60):
    # 调用is_breakthrough函数，判断是否突破60日平台
    return is_breakthrough(code_name=code_name,data=data,end_date=end_date,threshold=threshold)

def is_breakthrough(code_name, data, end_date=None, threshold=60):
    # 如果有截止日期，只保留截止日期之前的数据
    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    # 如果数据为空，返回False
    if data is None:
        return False

    # 只保留最近的threshold天数据
    data = data.tail(n=threshold)
    # 如果数据不足threshold天，返回False
    if len(data) < threshold:
        logging.debug(f"{code_name}:样本小于{threshold}天...\n")
        return False

    # 获取最近threshold天的最高收盘价和最大成交量
    max_price = data['收盘'].max()
    max_amount = data['成交量'].max()

    # 获取最近一天的收盘价和成交量
    last_close = data.iloc[-1]['收盘']
    last_amount = data.iloc[-1]['成交量']
    # 判断最近一天是否涨停
    is_limit = float(row['p_change']) > 9.5

    # 如果最近一天的收盘价突破了最近threshold天的最高收盘价，且最近一天的成交量较前期最大量萎缩，且最近一天涨停
    if (last_close >= max_price) and (last_amount < max_amount) and is_limit:
        # 返回True
        return True

    # 否则返回False
    return False
