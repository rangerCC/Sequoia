# -*- encoding: UTF-8 -*-
import logging
import settings

def check(code_name, data, end_date=None, threshold=60):
    # 判断股票代码是否在热门清单中
    def is_in_top_list():
        return code_name[0] in settings.top_list

    # 根据截止日期过滤数据
    def filter_data_by_end_date():
        if end_date is not None:
            mask = (data['日期'] <= end_date)
            return data.loc[mask]
        return data

    # 样本数量是否大于等于阈值
    def is_sample_size_valid():
        return len(data) >= threshold

    # 最低价的最小值是否小于等于最高价的1.9倍
    def is_ratio_increase_valid():
        low = data['最低'].min()
        ratio_increase = data.iloc[-1]['最高'] / low
        return ratio_increase >= 1.9

    # 是否存在连续的大涨
    def has_consecutive_large_increases():
        for i in range(1, len(data)):
            if data.iloc[i - 1]['p_change'] >= 9.5 and data.iloc[i]['p_change'] >= 9.5:
                return True
        return False

    # 如果不在热门清单中，返回False
    if not is_in_top_list():
        return False

    # 根据截止日期过滤数据
    data = filter_data_by_end_date()
    # 取最近的threshold天数据
    data = data.tail(n=threshold)

    # 如果样本数量小于阈值，返回False
    if not is_sample_size_valid():
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 取最近的14天数据
    data = data.tail(n=24).head(n=14)

    # 如果最低价的最小值小于等于最高价的1.9倍，返回False
    if not is_ratio_increase_valid():
        return False

    # 如果存在连续的大涨，返回True，否则返回False
    return has_consecutive_large_increases()
