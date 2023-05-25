# -*- encoding: UTF-8 -*-

import akshare as ak
import logging
import talib as tl

import concurrent.futures


def fetch_data(stock):
    # 获取股票数据
    data = ak.stock_zh_a_hist(symbol=stock, period="daily", start_date="20200101", adjust="qfq")
    # 如果数据为空，则跳过
    if data is None or data.empty:
        logging.debug("股票："+stock+" 没有数据，略过...")
        return None

    return data.astype({'成交量': 'double'})


def process_data(data):
    # 计算涨跌幅
    data['p_change'] = tl.ROC(data['收盘'], 1)
    return data


def fetch_stocks_data(stocks):
    # 使用线程池获取多只股票数据
    stocks_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_stock = {executor.submit(fetch_data, stock): stock for stock in stocks}
        for future in concurrent.futures.as_completed(future_to_stock):
            stock = future_to_stock[future]
            try:
                data = future.result()
                if data is not None:
                    data = process_data(data)
                    stocks_data[stock] = data
            except Exception as exc:
                handle_exception(stock, exc)

    return stocks_data


def handle_exception(stock, exc):
    # 处理异常
    print('%s(%r) generated an exception: %s' % (stock[1], stock[0], exc))


def run(stocks):
    # 获取多只股票数据
    return fetch_stocks_data(stocks)
