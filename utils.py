# -*- coding: UTF-8 -*-
import datetime
from pandas.tseries.offsets import *

import xlrd
import pandas as pd
import os
import settings


# 是否是工作日
def is_weekday():
    return datetime.datetime.today().weekday() < 5

# 过滤指定股票
def filter_stocks(stock_list):
    return [stock for stock in stock_list if (
        (stock[0] != None and stock[1] != None) and (
        stock[0].startswith('00') or
        stock[0].startswith('60') or
        stock[0].startswith('SZ00') or
        stock[0].startswith('SZ60') or
        stock[0].startswith('SH00') or
        stock[0].startswith('SH60')) and not (
        'ST' in stock[1] or
        '*'  in stock[1] or
        '退' in stock[1] or
        'N' in stock[1]))]