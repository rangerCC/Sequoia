# -*- encoding: UTF-8 -*-
import yaml  # 导入 yaml 库
import os  # 导入 os 库
import akshare as ak  # 导入 akshare 库
from wxpusher import WxPusher  # 导入 wxpusher 库

def init():
    global g_config, top_list  # 定义全局变量 g_config 和 top_list
    root_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录的绝对路径
    config_file = os.path.join(root_dir, 'config.yaml')  # 获取配置文件的绝对路径
    with open(config_file, 'r') as file:  # 打开配置文件
        g_config = yaml.safe_load(file)  # 读取配置文件内容并赋值给全局变量 g_config

    df = ak.stock_lhb_stock_statistic_em(symbol="近三月")  # 获取股票龙虎榜数据
    mask = df['买方机构次数'] > 1  # 获取买方机构次数大于 1 的股票
    top_list = df.loc[mask, '代码'].tolist()  # 将符合条件的股票代码转换为列表并赋值给全局变量 top_list

    if g_config['push']['enable']:  # 如果开启了推送功能
        WxPusher.default_token = g_config['push']['wxpusher_token']  # 设置 wxpusher 的 token
        update_users()  # 更新用户列表


def config():
    return g_config  # 返回全局变量 g_config


def update_users():
    if not g_config['push']['enable']:  # 如果没有开启推送功能
        return

    res = WxPusher.query_user(1, 1000)  # 获取用户列表
    if not res or res['code'] != 1000:  # 如果获取用户列表失败
        return

    users = res['data']['records']  # 获取用户列表
    uids = [user['uid'] for user in users if user.get('uid')]  # 获取用户 uid 列表
    if uids:  # 如果用户 uid 列表不为空
        g_config['push']['wxpusher_uids'] = uids  # 将用户 uid 列表赋值给全局变量 g_config 的 wxpusher_uids
