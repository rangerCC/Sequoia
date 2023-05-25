import talib as tl  # 导入 talib 库，用于计算技术指标
import pandas as pd  # 导入 pandas 库，用于数据处理
import logging  # 导入 logging 库，用于记录日志

def check(code_name, data, end_date=None, threshold=60):
    # 样本小于60天
    if len(data) < threshold:
        logging.debug(f"{code_name}: 样本小于{threshold}天...\n")  # 记录日志
        return False

    # 计算成交量5日均线
    data['vol_ma5'] = tl.MA(data['成交量'].values, 5)

    # 如果有截止日期，只保留截止日期之前的数据
    if end_date is not None:
        data = data[data['日期'] <= end_date]
    if data.empty:
        return False

    # 获取最后一天的涨跌幅
    p_change = data.iloc[-1]['p_change']
    if p_change > -9.5:
        return False

    # 取最近的threshold+1天数据
    data = data.tail(n=threshold + 1)
    if len(data) < threshold + 1:
        logging.debug(f"{code_name}: 样本小于{threshold+1}天...\n")  # 记录日志
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['收盘']
    # 最后一天成交量
    last_vol = data.iloc[-1]['成交量']

    # 成交额不低于2亿
    amount = last_close * last_vol * 100  # 计算成交额
    if amount < 200000000:
        return False

    # 取最近的threshold天数据
    data = data.head(n=threshold)

    # 获取最近5天的成交量均值
    mean_vol = data.iloc[-1]['vol_ma5']

    # 计算量比
    vol_ratio = last_vol / mean_vol  # 计算量比
    if vol_ratio >= 4:
        msg = f"*{code_name}\n量比：{vol_ratio:.2f}\t跌幅：{p_change}%\n"
        logging.debug(msg)  # 记录日志
        return True
    else:
        return False
