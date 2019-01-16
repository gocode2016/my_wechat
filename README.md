# 个人微信订阅号后台

## 订阅号名称
IT魔君，欢迎大家关注我

## 功能简介
1. 闲聊（和AI机器人尬聊，此功能适合苦逼的单身程序猿）
2. 远程控制（高端大气上档次，适合装逼耍酷）
3. 太忙，还没有做...

## 使用方法
1. git clone https://github.com/itmojun/my_wechat.git
2. cd my_wechat
3. pip install -r requirements.txt
4. gunicorn -w 4 -b 127.0.0.1:40002 main:app -D
5. 配置nginx反向代理
6. 微信订阅号后台设置服务器URL

