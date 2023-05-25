import datetime
import logging

import akshare as ak
from wxpusher import WxPusher

import push
import settings


def prepare():
    # 判断是否启用监控
    if not settings.config['monitor']['enable']:
        return

    # 获取前一天的日期
    dt = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    # 获取实时行情信息
    news_cctv_df = ak.news_cctv(date=dt)
    # 获取国内联播快讯
    fav_news = news_cctv_df.loc[(news_cctv_df['title'] == '国内联播快讯')]
    # 如果没有国内联播快讯则返回
    if fav_news.empty:
        return

    # 处理国内联播快讯
    process(dt, fav_news)


def process(dt, fav_news):
    # 构造消息
    msg = "【{} 国内联播快讯】\n".format(dt)
    # 拆分国内联播快讯
    split_news = fav_news['content'].iloc[0].split('。')
    for index, a_new in enumerate(split_news, start=1):
        if len(a_new) > 0:
            # 构造单条消息
            msg += '\n【{}】{}\n'.format(index, a_new)

    # 推送消息
    push.statistics(msg)
