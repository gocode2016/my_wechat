#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: dj
@contact: dj@itmojun.com
@software: PyCharm
@file: main.py
@time: 2018/12/5 20:32
"""

import time
import urllib, json, random
from flask import Flask, request, abort
from werkzeug.contrib.fixers import ProxyFix
import redis
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message, create_reply


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)


def get_robot_reply(input_text):
    apiKeys = ('cc8c863cfa2b42ecb1e6ae9d4f2c5f36', '512a756fbb5b45b4902e53e09a89e86d', '263aa1a1b0a6470d84ad28415e7bee47', '2d7072e72426447585a3bfc5f72fdc38', 'f7954cb3d7b14134962d0a918185339a') 

    data = {
        "reqType":0,
        "perception": {
            "inputText": {
                "text": input_text
            },
        },
        "userInfo": {
            "apiKey": random.choice(apiKeys),
            "userId": "339745"
        }
    }

    data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    url = urllib.request.Request("http://openapi.tuling123.com/openapi/api/v2", data=data, method="POST")
    res = urllib.request.urlopen(url).read()
    return json.loads(res.decode("utf-8"))["results"][0]["values"]["text"]


@app.route('/wx', methods=['GET', 'POST'])
def weixin_handle():
    token = 'itmojun'  # 注意此处要与微信公众平台上填写的保持一致
    timestamp = request.args.get('timestamp', '')  
    nonce = request.args.get('nonce', '')  
    echo_str = request.args.get('echostr', '')  
    signature = request.args.get('signature', '')  

    try:  
        check_signature(token, signature, timestamp, nonce)  
    except InvalidSignatureException:
        # 处理异常情况或忽略
        abort(403)  # 后续代码不会被执行

    if request.method == 'GET':
        # 微信公众号后台设置界面提交服务器URL验证
        return echo_str  
        # return reply, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        # 微信官方服务器通过POST方式转发消息给我们自己的服务器
        msg = parse_message(request.data)

        r = redis.Redis(connection_pool=pool)
        redis_key = msg.source

        if msg.type == 'event':  # 事件消息
            if msg.event == 'subscribe':  # 关注事件
                subscribe_time = msg.create_time.strftime("%Y-%m-%d %H:%M:%S")
                ret = r.hmset(redis_key, {"state": 1, "subscribe_time": subscribe_time})
                if ret:
                    pass  # redis操作成功
                else:
                    pass  # redis操作失败

                reply = create_reply('Hello，小伙伴儿，欢迎关注IT魔君！一入IT深似海，从此再也不缺爱，IT魔君与你分享各种骚操作，带你装逼带你飞！', msg);
            elif msg.event == 'unsubscribe':  # 取消关注事件
                r.delete(redis_key)
                reply = create_reply('期待与你再次相遇！', msg)
            else:
                # 比如点击菜单事件等
                reply = create_reply('', msg)  # 回复空消息
        elif msg.type == 'text' or msg.type == 'voice':  # 文本消息或语音消息
            cur_msg_time = time.time()
            last_msg_time = r.hget(redis_key, 'last_msg_time')  # hget方法返回值为str值或者None 
            if not last_msg_time:
                last_msg_time = 0
            ret = r.hset(redis_key, "last_msg_time", cur_msg_time)

            # 如果两次连续消息的时间间隔超过1小时，那么就直接设置为普通聊天模式
            if cur_msg_time - float(last_msg_time) > 3600:
                r.hmset(redis_key, {'state': 1})
                state = '1'
            
            if msg.type == 'voice':
                content = msg.recognition
                if content is None:
                    reply = create_reply('你的普通话不够标准，请再说一次或打字吧！', msg)
                    return reply.render()
            else:
                content = msg.content

            state = r.hget(redis_key, 'state')  # hget方法返回值为str值或者None 
            if not state:
                r.hmset(redis_key, {'state': 1})
                state = '1'

            if state == '1':
                # 普通聊天模式
                if '急急如律令' in content:
                    if r.hexists(redis_key, 'pc_id'):
                        reply = '成功进入远控模式！(已绑定目标电脑ID为“%s”，如需更换绑定，请输入“绑定电脑”)' % r.hget(redis_key, 'pc_id')
                        ret = r.hset(redis_key, "state", 2)
                    else:
                        reply = '成功进入远控模式，请输入要绑定的目标电脑ID'
                        ret = r.hset(redis_key, "state", 21)
                # elif '小魔仙你好' in content:
                elif '@小魔仙' == content:
                        reply = '小魔仙驾到，我们开始快乐地尬聊吧~'
                        ret = r.hset(redis_key, "state", 3)
                else:
                        # reply = ''  # 回复空消息
                        reply = '君哥正在苦逼调bug，稍后给你回复！'
            elif state == '2':
                # 远控模式
                if '芝麻关门' in content:
                    reply = '已退出远控模式，进入与君哥尬聊的快乐模式！'
                    ret = r.hset(redis_key, "state", 1)
                elif '绑定电脑' in content:
                    reply = '目标电脑ID是啥？'
                    ret = r.hset(redis_key, "state", 21)
                else:
                    pc_id = r.hget(redis_key, 'pc_id')
                    cmd = content
                    ret = r.set(pc_id, cmd, ex=3)  # 过期时间为3秒
                    if ret:
                        reply = '控制成功！'
                    else:
                        reply = '控制失败！'
            elif state == '21':
                # 等待用户输入目标电脑ID模式
                pc_id = content
                ret = r.hmset(redis_key, {'state': 2, 'pc_id': pc_id})
                if ret:
                    reply = '绑定成功！'
                else:
                    reply = '绑定失败！'
            elif state == '3':
                # 自动聊天模式
                # if '小魔仙再见' in content:
                if '@君哥' == content:
                    reply = '小魔仙睡觉去了，现在君哥陪你尬聊！'
                    ret = r.hset(redis_key, "state", 1)
                else:
                    try:
                        reply = get_robot_reply(content)
                    except Exception as e:
                        reply = str(e)
            else:
                reply = ''  # 回复空消息

            reply = create_reply(reply, msg)  
        else:  # 其他类型消息
            reply = create_reply('很抱歉，我暂时不能处理这种消息！', msg)  
        
        return reply.render()  


if __name__ == '__main__':
    app.run(debug=True)

