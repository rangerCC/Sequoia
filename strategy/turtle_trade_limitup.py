# -*- coding: UTF-8 -*-

import logging

# 最后一个交易日收市价为指定区间内最高价
def check(code_name, data, end_date=None, threshold=60):
    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    if data is None:
        return False
    
    data = data.tail(n=threshold)
    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False
    
    max_price = 0
    max_amount = 0

    for index, row in data.iterrows():
        if row['收盘'] > max_price:
            max_price = float(row['收盘'])
        if row['成交量'] > max_amount:
            max_amount = float(row['成交量'])

    last_close = data.iloc[-1]['收盘']
    last_amount = data.iloc[-1]['成交量']
    is_limit = float(row['p_change']) > 9.5

    # 突破60日平台且涨停且成交量较前期最大量萎缩
    if (last_close >= max_price) and (last_amount < max_amount) and (is_limit==True):
        return True

    return False
