'''
Descripttion: 
version: 
Author: Catop
Date: 2021-02-24 22:20:18
LastEditTime: 2021-02-24 22:27:50
'''
#coding:utf-8
import requests


def sendMsg(user_id,message):
    url = 'http://127.0.0.1:5801/send_private_msg'
    data = {'user_id':user_id,'message':message}
    res = requests.get(url,params=data)
    print(f"回复私聊消息@{user_id}：{message[:20]}")
    return res.text

def add_request(request_flag):
    url = 'http://127.0.0.1:5801/set_friend_add_request'
    data = {'flag':str(request_flag)}
    res = requests.get(url,params=data)
    print("加好友成功")
    return res.text
