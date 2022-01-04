import qqbot
from qqbot import Message
from config import *
import random, re
import httpx
from jike_util import jike_post

token = qqbot.Token(app_id, token)
api = qqbot.UserAPI(token, False)
user = api.me()
print(user.username + 'has logged in.')  # 打印机器人名字
msg_api = qqbot.MessageAPI(token, False)

def send_msg(content, message):
    send = qqbot.MessageSendRequest(content, message.id)
    msg_api.post_message(message.channel_id, send)

def save_to_flomo(msg):
    post_data = {
        'content': msg
    }
    header = {
        'Content-type': 'application/json'
    }
    res = httpx.post(url=flomo_api_url, json=post_data)
    return res.status_code

# 定义注册事件回调执行函数,如 `_message_handler`
def _at_message_handler(event, message: Message):
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    send = qqbot.MessageSendRequest("<@%s>叫我干嘛？" % message.author.id, message.id)
    msg_api.post_message(message.channel_id, send)

def _message_handler(event, message: Message):
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    msg = message.content
    if msg.startswith("抽签 "):
        choice_list = msg.split(' ')[1:]
        # send = qqbot.MessageSendRequest("<@%s>谢谢你，加油" % message.author.id, message.id)
        send = qqbot.MessageSendRequest("<@{}> {}".format(message.author.id, random.choice(choice_list)), message.id)
        msg_api.post_message(message.channel_id, send)
    if '#' in msg and len(msg) > 20 and message.author.id == owner_id:
        status_code = save_to_flomo(msg)
        if status_code == 200:
            send_msg("<@{}> {}".format(message.author.id, 'saved to flomo'), message)
        else:
            send_msg("<@{}> {}".format(message.author.id, 'save to flomo failed'), message)
    if '.jike' in msg and message.author.id == owner_id:
        result = jike_post(msg)
        if result['success']:
            send_msg("<@{}> {}".format(message.author.id, 'send to jike succeed'), message)
        else:
            send_msg("<@{}> {}".format(message.author.id, 'send to jike failed, error code: {}'.format(result['error'])), message)

at_event_handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _at_message_handler)
msg_event_handler = qqbot.Handler(qqbot.HandlerType.MESSAGE_EVENT_HANDLER, _message_handler)
qqbot.listen_events(token, False, at_event_handler, msg_event_handler)


