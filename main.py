# 导入需要使用的模块
import utils
import logging
import work_flow
import stock_monitor
import everyday_news
import settings
import schedule
import time

# 定义每日要闻的准备函数
def prepare_everyday_news():
    # 调用每日要闻的准备函数
    everyday_news.prepare()

# 定义工作流的准备函数
def prepare_work_flow():
    # 如果是工作日，则准备工作流
    if utils.is_weekday():
        work_flow.prepare()

# 定义股票监控的准备函数
def prepare_stock_monitor():
    # 准备股票监控
    stock_monitor.prepare()
    # 如果是工作日，则准备个股监控
    if utils.is_weekday():
        stock_monitor.prepare()

# 配置 Logger 日志
logging.basicConfig(format='%(asctime)s %(message)s', filename='result.log')
logging.getLogger().setLevel(logging.INFO)

# 初始化配置
settings.init()

# 如果配置中开启了定时任务
if settings.config['cron']:
    # 实时监控
    # 定义个股监控的时间间隔
    timeinterval = settings.config['monitor']['timeinterval']
    # 每隔一定时间就准备股票监控
    schedule.every(timeinterval).seconds.do(prepare_stock_monitor)

    # 定义优质股挖掘的时间
    # schedule.every().day.at("15:10").do(prepare_work_flow)

    # 循环执行定时任务
    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    # 实时任务
    # 准备工作流
    prepare_work_flow()
    # 准备股票监控
    prepare_stock_monitor()
