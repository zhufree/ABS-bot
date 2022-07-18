import qqbot
from qqbot import Message, MessageSendRequest
from config import *
import random, time
import httpx
from jike_util import jike_post
from rss_util import parse_rss

BASE_URL = 'https://free-rss-zhufree.vercel.app/'
last_query_time = time.time() - 60*5
query_lock = False

rss_self_list = [
    BASE_URL + 'weibo/user/' + weibo_id, # weibo，比实际时间早8h
    BASE_URL + 'jike/user/' + jike_id # jike, 比实际时间早8h
]

token = qqbot.Token(app_id, token)
api = qqbot.UserAPI(token, False)
user = api.me()
print(user.username + 'has logged in.')  # 打印机器人名字
msg_api = qqbot.MessageAPI(token, False)


def send_msg_to_channel(msg, channel_id=self_channel_id):
    send = MessageSendRequest(msg)
    msg_api.post_message(channel_id, send)

def send_msg_to_channel(msg, img_url, channel_id=self_channel_id):
    send = MessageSendRequest(msg, image=img_url)
    msg_api.post_message(channel_id, send)


def reply_msg(content, message, img_url=None):
    if img_url:
        send = MessageSendRequest(content, message.id, image=img_url)
    else:
        send = MessageSendRequest(content, message.id)
    msg_api.post_message(message.channel_id, send)


def check_statues(message):
    global last_query_time
    global query_lock
    if query_lock:
        return
    query_lock = True
    if time.time() - last_query_time > 60*10:
        try:
            for url in rss_self_list:
                results = parse_rss(url, last_query_time)
                for result in results:
                    content = '''{}\nat {}'''.format(result['content'], result['time'])
                    if len(result['img_urls']) > 0:
                        reply_msg(content, result['img_urls'][0], message)
                    else:
                        reply_msg(content, message)
               
        finally:
            last_query_time = time.time()
            query_lock = False


def save_to_flomo(msg):
    post_data = {
        'content': msg
    }
    res = httpx.post(url=flomo_api_url, json=post_data)
    return res.status_code

# 定义注册事件回调执行函数,如 `_message_handler`
def _at_message_handler(event, message: Message):
    send = qqbot.MessageSendRequest("<@%s>叫我干嘛？" % message.author.id, message.id)
    msg_api.post_message(message.channel_id, send)

def _message_handler(event, message: Message):
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    msg = message.content
    attachments = []
    if 'attachments' in dir(message):
        attachments = ['https://' + a.url for a in message.attachments]
    if msg.startswith("抽签 "):
        choice_list = msg.split(' ')[1:]
        # send = qqbot.MessageSendRequest("<@%s>谢谢你，加油" % message.author.id, message.id)
        send = qqbot.MessageSendRequest("<@{}> {}".format(message.author.id, random.choice(choice_list)), message.id)
        msg_api.post_message(message.channel_id, send)
    if '#' in msg and len(msg) > 20 and message.author.id == owner_id:
        status_code = save_to_flomo(msg)
        if status_code == 200:
            reply_msg("<@{}> {}".format(message.author.id, 'saved to flomo'), message)
        else:
            reply_msg("<@{}> {}".format(message.author.id, 'save to flomo failed'), message)
    if '.jike' in msg and message.author.id == owner_id:
        result = jike_post(msg.replace('.jike', ''), attachments)
        if result['success']:
            reply_msg("<@{}> {}".format(message.author.id, 'send to jike succeed'), message)
        else:
            reply_msg("<@{}> {}".format(message.author.id, 'send to jike failed, error code: {}'.format(result['error'])), message)

at_event_handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _at_message_handler)
msg_event_handler = qqbot.Handler(qqbot.HandlerType.MESSAGE_EVENT_HANDLER, _message_handler)
qqbot.listen_events(token, False, at_event_handler, msg_event_handler)
send_msg_to_channel("tet")

