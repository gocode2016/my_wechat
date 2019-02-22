# 个人微信公众号后台

## 公众号信息
公众号名称：IT魔君

二维码图片：

![IT魔君公众号二维码](https://raw.githubusercontent.com/itmojun/static_resources/master/IT魔君公众号二维码(最小尺寸).jpg)

欢迎各位小伙伴儿关注我！

## 功能简介
1. 闲聊（和AI机器人尬聊，此功能适合苦逼的单身程序猿）

   在公众号中(普通聊天模式)发送“@小魔仙”，就可以进入自动聊天模式，发送“@君哥”或者超过1小时没有发送任何文本和语音消息，就可以退出自动聊天模式，回到普通聊天模式

2. 远程控制（高端大气上档次，适合装逼耍酷）

   在公众号中(普通聊天模式)发送“急急如律令”，就可以进入远控模式，发送“芝麻关门”或者超过1小时没有发送任何文本和语音消息，就可以退出远控模式，回到普通聊天模式

3. 普通聊天（用于君哥和粉丝尬聊）

4. 太忙，还没有做...

## 部署方法
1. git clone https://github.com/itmojun/my_wechat.git
2. cd my_wechat
3. pip install -r requirements.txt
4. gunicorn -w 4 -b 127.0.0.1:40002 main:app -D
5. 配置nginx反向代理
6. 微信订阅号后台设置服务器URL

