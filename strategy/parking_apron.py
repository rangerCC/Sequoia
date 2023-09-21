# -*- encoding: UTF-8 -*-

import logging
from strategy import turtle_trade
import talib as tl
import pandas as pd

# “停机坪”策略
def check(code_name, data, end_date=None, threshold=30):
    data['ma5'] = pd.Series(tl.MA(data['收盘'].values, 5), index=data.index.values)
    data['ma10'] = pd.Series(tl.MA(data['收盘'].values, 10), index=data.index.values)

    origin_data = data

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return

    data = data.tail(n=threshold)

    flag = False

    # 找出涨停日
    for index, row in data.iterrows():
        try:
            if float(row['p_change']) > 9.5:
                if turtle_trade.check_enter(code_name, origin_data, row['日期'], threshold):
                    if check_internal(code_name, data, row):
                        flag = True
        except KeyError as error:
            logging.debug("{}处理异常：{}".format(code_name, error))

    return flag


def check_internal(code_name, data, limitup_row):
    limitup_price = limitup_row['收盘']
    limitup_end = data.loc[(data['日期'] > limitup_row['日期'])]
    limitup_end = limitup_end.head(n=3)
    
    if len(limitup_end.index) < 3:
        return False

    consolidation_day1 = limitup_end.iloc[0]
    consolidation_day23 = limitup_end = limitup_end.tail(n=2)

    # 涨停突破后第一天，开盘价/收盘价在-3%~+3%范围
    if not(consolidation_day1['收盘'] > limitup_price and consolidation_day1['开盘'] > limitup_price and
        0.97 < consolidation_day1['收盘'] / consolidation_day1['开盘'] < 1.03):
        return False

    #  成交量： (row['成交量'] / limitup_row['成交量']) < 0.5
    for index, row in consolidation_day23.iterrows():
        try:
            if row['收盘']<row['ma10']: # 10日均线以上
                return False
            if not (0.97 < (row['收盘'] / row['开盘']) < 1.03 and -5 < row['p_change'] < 5
                    and row['收盘'] > limitup_price and row['开盘'] > limitup_price):
                return False
        except KeyError as error:
            logging.debug("{}处理异常：{}".format(code_name, error))

    logging.debug("股票{0} 涨停日期：{1}".format(code_name, limitup_row['日期']))

    return True

