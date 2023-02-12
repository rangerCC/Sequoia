# -*- encoding: UTF-8 -*-

import logging
import settings
from wxpusher import WxPusher

def push(msg):
    if settings.config['push']['enable']:
        uids = settings.config['push']['wxpusher_uids']
        token = settings.config['push']['wxpusher_token']
        if not (len(uids)==0 and len(token)==0) :
            response = WxPusher.send_message(msg, uids=uids,token=token)
            print(response)
    logging.info(msg)


def statistics(msg=None):
    push(msg)


def strategy(msg=None):
    if msg is None or not msg:
        msg = '今日没有符合条件的股票'
    push(msg)
