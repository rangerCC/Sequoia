# -*- coding: UTF-8 -*-
import datetime

# 判断股票是否有效的函数
def is_stock_valid(stock):
    # 定义有效的股票代码前缀
    valid_prefixes = ['00', '60', 'SZ00', 'SZ60', 'SH00', 'SH60']
    # 定义无效的股票名称子字符串
    invalid_substrings = ['ST', '*', '退', 'N']

    # 判断股票代码和名称是否为空
    if stock[0] is None or stock[1] is None:
        return False

    # 判断股票代码是否以有效前缀开头
    if not any(stock[0].startswith(prefix) for prefix in valid_prefixes):
        return False

    # 判断股票名称是否包含无效子字符串
    if any(substring in stock[1] for substring in invalid_substrings):
        return False

    # 如果以上条件都不满足，说明股票有效
    return True

# 判断当前日期是否为工作日的函数
def is_weekday():
    return datetime.datetime.today().weekday() < 5

# 过滤股票列表，只保留有效股票的函数
def filter_stocks(stock_list):
    return [stock for stock in stock_list if is_stock_valid(stock)]
