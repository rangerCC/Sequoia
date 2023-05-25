# -*- encoding: UTF-8 -*-

import logging
import settings
from wxpusher import WxPusher

def push(msg, push_type=0):
    """
    发送推送消息
    :param msg: 推送消息内容
    :param push_type: 推送类型，0：全员推送；1：topic 推送；2：付费 topic 推送
    """
    # 如果推送未开启，则直接返回
    if not settings.config['push']['enable']:
        return
    # 获取微信推送的 token
    token = settings.config['push']['wxpusher_token']
    # 如果 token 不存在，则直接返回
    if not token:
        return
    # 获取微信推送的 topic
    topics = settings.config['push']['wxpusher_topics'] if push_type > 0 else []
    # 获取微信推送的 uid
    uids = settings.config['push']['wxpusher_uids'] if push_type == 0 else []
    # 如果是付费 topic 推送，则需要验证支付
    verify_pay = 1 if push_type > 1 else 0
    # 发送消息并记录日志
    response = WxPusher.send_message(msg, token=token, uids=uids, topic_ids=topics, verifyPay=verify_pay)
    logging.info(msg)
    print(response)


def statistics(msg=None, push_type=0):
    """
    发送统计消息
    :param msg: 统计消息内容
    :param push_type: 推送类型，0：全员推送；1：topic 推送；2：付费 topic 推送
    """
    # 调用 push 函数发送消息
    push(msg, push_type)


def strategy(msg=None, push_type=0):
    """
    发送策略消息
    :param msg: 策略消息内容
    :param push_type: 推送类型，0：全员推送；1：topic 推送；2：付费 topic 推送
    """
    # 如果消息为空，则默认发送“今日没有符合条件的股票”
    if not msg:
        msg = '今日没有符合条件的股票'
    # 调用 push 函数发送消息
    push(msg, push_type)
