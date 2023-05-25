# -*- encoding: UTF-8 -*-
import logging

def check(code_name, data, end_date=None, threshold=60):
    # 如果指定了 end_date，则只取 end_date 之前的数据
    if end_date is not None:
        data = data[data['日期'] <= end_date]

    # 取最近 threshold 天的数据
    data = data.tail(threshold)

    # 样本小于 threshold 天，返回 False
    if len(data) < threshold:
        logging.debug(f"{code_name}: 样本小于{threshold}天...\n")
        return False

    # 计算最近 threshold 天的涨幅
    ratio_increase = (data.iloc[-1]['收盘'] - data.iloc[0]['收盘']) / data.iloc[0]['收盘']

    # 涨幅小于 0.6，返回 False
    if ratio_increase < 0.6:
        return False

    # 允许有一次“洗盘”
    wash_count = 0
    for i in range(1, len(data)):
        # 单日跌幅超 7%
        if data.iloc[i - 1]['p_change'] < -7:
            return False

        # 高开低走超 7%
        if (data.iloc[i]['收盘'] - data.iloc[i]['开盘']) / data.iloc[i]['开盘'] * 100 < -7:
            return False

        # 两日累计跌幅超 10%
        if data.iloc[i - 1]['p_change'] + data.iloc[i]['p_change'] < -10:
            if wash_count == 0:
                wash_count += 1
            else:
                return False

        # 两日高开低走累计超 10%
        if (data.iloc[i]['收盘'] - data.iloc[i - 1]['开盘']) / data.iloc[i - 1]['开盘'] * 100 < -10:
            if wash_count == 0:
                wash_count += 1
            else:
                return False

    return True
