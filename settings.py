# -*- encoding: UTF-8 -*-
import yaml
import os
import akshare as ak
from wxpusher import WxPusher

def init():
    global config
    global top_list
    root_dir = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
    config_file = os.path.join(root_dir, 'config.yaml')
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    df = ak.stock_lhb_stock_statistic_em(symbol="近三月")
    mask = (df['买方机构次数'] > 1)  # 机构买入次数大于1
    df = df.loc[mask]
    top_list = df['代码'].tolist()
    
    # 更新用户列表
    update_users()


def config():
    return config


def update_users() :
    WxPusher.default_token = config['push']['wxpusher_token']
    res = WxPusher.query_user(1, 1000)
    if (not res) or (not res['code'] == 1000) :
        return

    users_count = res['data']['total']
    users = res['data']['records']
    if (not users) or (len(users) <= 0) :
        return
    
    uids = []
    for user in users :
        if len(user['uid']) > 0 :
            uids.append(user['uid'])
    if len(uids) > 0 :
        config['wxpusher_uids'] = uids