# -*- encoding: UTF-8 -*-

import utils
import logging
import work_flow
import stock_monitor
import everyday_news
import settings
import schedule
import time

def job0():
    everyday_news.prepare()

def job1():
    work_flow.prepare()
    # if utils.is_weekday():
    #     work_flow.prepare()

def job2():
    stock_monitor.prepare()
    # if utils.is_weekday():
    #     stock_monitor.prepare()


logging.basicConfig(format='%(asctime)s %(message)s', filename='result.log')
logging.getLogger().setLevel(logging.INFO)
settings.init()

# 每日要闻
# job0()

if settings.config['cron']:
    # 实时监控

    # 个股监控
    timeinterval = settings.config['monitor']['timeinterval']
    schedule.every(timeinterval).seconds.do(job2)

    # 优质股挖掘
    # schedule.every().day.at("15:10").do(job1)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    # 实时任务
    job1()
    # job2()
