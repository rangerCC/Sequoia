# -*- encoding: UTF-8 -*-

import data_fetcher
import settings
import utils
import strategy.enter as enter
from strategy import turtle_trade, climax_limitdown
from strategy import backtrace_ma10
from strategy import backtrace_ma20
from strategy import backtrace_ma55
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_backtrace_increase
from strategy import keep_increasing
from strategy import high_tight_flag
from strategy import turtle_trade_limitup
import akshare as ak
import push
import logging
import time
from datetime import datetime,timedelta

def prepare():
    logging.info("\n************************ process start ***************************************\n\n")
    process_informations()
    process_strategies()
    logging.info("\n************************ process   end ***************************************\n")


def process_informations() :
    dt = statistics_latest()
    statistics_stocks(dt)
    statistics_youzi(dt)
    # statistics_guanzhu(dt)


def process_strategies() :
    all_data = ak.stock_zh_a_spot_em() # 实时行情
    subset = all_data[['代码', '名称', '涨跌幅']]
    stocks = [tuple(x) for x in subset.values]
    stocks = utils.filter_stocks(stocks)

    strategies = {
        '今日高而窄旗形': high_tight_flag.check,
        # '今日托底回踩55日均线': backtrace_ma55.check,
        '今日回踩年线': backtrace_ma250.check,
        '均线多头': keep_increasing.check,
        '放量上涨': enter.check_volume,
        # '突破平台': breakthrough_platform.check,
        # '无大幅回撤': low_backtrace_increase.check,
        # '放量跌停': climax_limitdown.check,
        '涨停大海龟': turtle_trade_limitup.check,
        '经典停机坪': parking_apron.check,
        '低吸超短牛': backtrace_ma10.check,
        '低吸短线牛': backtrace_ma20.check,
        '波段牛': backtrace_ma55.check,
        '长线牛': backtrace_ma250.check,
        # '近期突破牛': backtrace_ma10.check,
    }

    # 依次处理策略
    stocks_data = data_fetcher.run(stocks)
    for strategy, strategy_func in strategies.items():
        check(stocks_data, strategy, strategy_func)
        time.sleep(2)


def check(stocks_data, strategy, strategy_func):
    end = settings.config['end_date']
    m_filter = check_enter(end_date=end, strategy_fun=strategy_func)
    results = dict(filter(m_filter, stocks_data.items()))
    if len(results) > 0:
        stock_msg = "|股票代码      股票名称      涨跌幅      行业      流通值|\n"
        for stock in list(results.keys()) :
            if stock[0] in ('600068') :
                continue

            stock_data = ak.stock_individual_info_em(symbol=stock[0])
            industry = stock_data.loc[stock_data['item']=='行业'].value.iloc[0]
            equity = stock_data.loc[stock_data['item']=='流通市值'].value.iloc[0]
            if equity == '-' :
                equity = 0
            else :
                equity = float(equity)/100000000.0
            stock_msg = stock_msg + "|{}       {}      {}      {}      {:.2f}亿|\n".format(stock[0],stock[1],stock[2],industry,equity)

            # 股东数
            # stock_zh_a_gdhs_detail_em_df = ak.stock_zh_a_gdhs_detail_em(symbol=stock[0])
            # print(stock_zh_a_gdhs_detail_em_df)
            
        push.strategy('【{0}】\n\n{1}\n\n'.format(strategy, stock_msg))


def check_enter(end_date=None, strategy_fun=enter.check_volume):
    def end_date_filter(stock_data):
        if end_date is not None:
            if end_date < stock_data[1].iloc[0].日期:  # 该股票在end_date时还未上市
                logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                return False
        return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)

    return end_date_filter


# 大盘统计数据
def statistics_latest():
    msg = "【今日A股】\n"

    # 大盘概览
    msg = msg + "\n>>>>>>>>>>>> 大盘概览\n"
    stock_market_activity = ak.stock_market_activity_legu()
    for index, row in stock_market_activity.iterrows() :
        if row[0] == '活跃度' or row[0] == '统计日期':
            msg = msg + "{}：{}\n".format(row[0],row[1])
        else :
            msg = msg + "{}：{}\n".format(row[0],int(row[1]))

    push.statistics(msg)

    return stock_market_activity.iloc[11][1].split(' ')[0]

# 游资、股东统计数据
def statistics_youzi(dt):
    msg = "【今日A股游资、股东追踪】\n"

    # 内部交易
    msg = msg + "\n>>>>>>>>>>>> 内部交易\n"
    stock_inner_trade_xq_df = ak.stock_inner_trade_xq()
    subset = stock_inner_trade_xq_df[['股票代码', '股票名称', '变动日期', '变动人', '变动股数', '成交均价']]
    subset_stocks = [tuple(x) for x in subset.values]
    subset_stocks = utils.filter_stocks(subset_stocks)
    for stock in subset_stocks :
        if stock[4] > 0 :
            lowest_date_diff = datetime.date(datetime.strptime(dt, '%Y-%m-%d')) - \
                stock[2]
            if timedelta(days=0) <= lowest_date_diff <= timedelta(days=3):
                msg = msg + "{} {}，{} 于 {} 以均价 {} 买入 {} 股\n".format(stock[0],stock[1],stock[3],stock[2],stock[5],stock[4])
                
    # 营业部买入追踪
    msg = msg + "\n>>>>>>>>>>>> 营业部买入追踪\n"
    stock_lhb_jgzz_sina_df = ak.stock_lhb_jgzz_sina(recent_day="5") #最近5日
    subset = stock_lhb_jgzz_sina_df[['股票代码', '股票名称', '累积买入额', '买入次数', '累积卖出额', '卖出次数', '净额']]
    subset_stocks = [tuple(x) for x in subset.values]
    subset_stocks = utils.filter_stocks(subset_stocks)
    for stock in subset_stocks :
        if stock[2] > 0 and stock[6]/stock[2] > 0.8:
            msg = msg + "{} {}，累计买入 {}w\n".format(stock[0],stock[1],stock[6])

    # 营业部上榜追踪
    msg = msg + "\n>>>>>>>>>>>> 营业部上榜追踪\n"
    stock_lhb_yytj_sina_df = ak.stock_lhb_yytj_sina(recent_day="5")
    subset = stock_lhb_yytj_sina_df[['营业部名称', '累积购买额', '累积卖出额', '买入前三股票']]
    subset_stocks = [tuple(x) for x in subset.values]
    for stock in subset_stocks :
        if stock[1] > 0 and stock[2]/stock[1] < 0.3 and stock[1]<2000:
            msg = msg + "{} 累计买入 {}w，买入前三票为：{}\n".format(stock[0], stock[1], stock[3])

    push.statistics(msg)


# 近1周和一月股票关注舆情
def statistics_guanzhu(dt):
    msg = "【近期热搜个股】\n"

    # 近一周热搜
    msg = msg + "\n>>>>>>>>>>>> 近一周热搜\n"
    stock_js_weibo_report_df_week = ak.stock_js_weibo_report(time_period="CNDAY7")
    subset = stock_js_weibo_report_df_week[['name', 'rate']]
    subset_stocks = [tuple(x) for x in subset.values]
    subset_stocks = sorted(subset_stocks, key=lambda x: x[1])
    msg = msg + "股票\t热度\n"
    for stock in subset_stocks :
        msg = msg + "{}\t{}\n".format(stock[0], stock[1])
    
    # 近一月热搜
    msg = msg + "\n>>>>>>>>>>>> 近一月热搜\n"
    stock_js_weibo_report_df_month = ak.stock_js_weibo_report(time_period="CNDAY30")
    subset = stock_js_weibo_report_df_month[['name', 'rate']]
    subset_stocks = [tuple(x) for x in subset.values]
    subset_stocks = sorted(subset_stocks, key=lambda x: x[1])
    msg = msg + "股票\t热度\n"
    for stock in subset_stocks :
        msg = msg + "{}\t{}\n".format(stock[0], stock[1])

    push.statistics(msg)


# 个股统计数据
def statistics_stocks(dt):
    msg = "【今日A股个股追踪】\n"

    # 持续缩量
    msg = msg + "\n>>>>>>>>>>>> 连续缩量1周及以上\n"
    stock_rank_cxsl_ths_df = ak.stock_rank_cxsl_ths()
    subset = stock_rank_cxsl_ths_df[['股票代码', '股票简称', '涨跌幅', '成交量', '缩量天数', '阶段涨跌幅', '所属行业']]
    subset_stocks = [tuple(x) for x in subset.values]
    subset_stocks = utils.filter_stocks(subset_stocks)
    for stock in subset_stocks :
        if stock[4] >= 7 :
            msg = msg + "{} {}，连续缩量{}天，{}\n".format(stock[0],stock[1],stock[4],stock[6])

    # 量价齐跌
    # msg = msg + "\n>>>>>>>>>>>> 量价齐跌\n"
    # stock_rank_ljqd_ths_df = ak.stock_rank_ljqd_ths()
    # subset = stock_rank_ljqd_ths_df[['股票代码', '股票简称', '量价齐跌天数', '阶段涨幅', '累计换手率', '所属行业']]
    # subset_stocks = [tuple(x) for x in subset.values]
    # subset_stocks = filter_stocks(subset_stocks)
    # for stock in subset_stocks :
    #     if stock[2] > 3 and stock[4]>50 :
    #         msg = msg + "{} {}，量价齐跌{}天，累计换手{}%，{}\n".format(stock[0],stock[1],stock[2],stock[4],stock[5])

    # 盘口异动
    # stock_changes_em_df = ak.stock_changes_em(symbol="大笔买入") # '火箭发射', '大笔买入', '大笔卖出'
    # print(stock_changes_em_df)

    # 个股上榜追踪
    # stock_lhb_ggtj_sina_df = ak.stock_lhb_ggtj_sina(recent_day="5")
    # subset = stock_lhb_ggtj_sina_df[['股票代码', '股票名称', '累积买入额', '买入次数', '累积卖出额', '卖出次数', '净额']]
    # subset_stocks = [tuple(x) for x in subset.values]
    # subset_stocks = utils.filter_stocks(subset_stocks)
    # print(stock_lhb_ggtj_sina_df)

    push.statistics(msg)
