# -*- encoding: UTF-8 -*-
import data_fetcher
import settings
import utils
import akshare as ak
from wxpusher import WxPusher
import push
import logging
import time
import datetime

def prepare():
    if not settings.config['monitor']['enable'] :
        return

    dt = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    # 实时行情信息
    news_cctv_df = ak.news_cctv(date=dt)
    fav_news = news_cctv_df.loc[(news_cctv_df['title'] == '国内联播快讯')]
    if not fav_news.empty :
        process(fav_news)


def process(fav_news):
    msg = "【国内联播快讯】\n"
    split_news = fav_news['content'].iloc[0].split('。')
    index = 1
    for a_new in split_news :
        msg = msg + '\n【{}】{}\n'.format(index, a_new)
    push.statistics(msg)

    # 个股信息
    # stock_individual_info_em_df = ak.stock_individual_info_em(symbol=code)
    
    
