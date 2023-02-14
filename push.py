# -*- encoding: UTF-8 -*-

import logging
import settings
from wxpusher import WxPusher

def push(msg,type=0):
    # type=0，全员推送；type=1，topic 推送；type=2，付费 topic 推送
    if settings.config['push']['enable']:
        token = settings.config['push']['wxpusher_token']
        topics = []
        uids = []
        verifyPay = 0
        if type == 0 :
            uids = settings.config['push']['wxpusher_uids']
            topics = settings.config['push']['wxpusher_topics']
        if type > 0 :
            topics = settings.config['push']['wxpusher_topics']
        if type > 1 :
            verifyPay = 1
        if not (len(token)==0) :
            response = WxPusher.send_message(msg, token=token, uids=uids, topic_ids=topics, verifyPay=verifyPay)
            print(response)
    logging.info(msg)


def statistics(msg=None,type=0):
    push(msg,type)


def strategy(msg=None,type=0):
    if msg is None or not msg:
        msg = '今日没有符合条件的股票'
    push(msg,type)
