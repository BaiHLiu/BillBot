'''
Descripttion: 
version: 
Author: Catop
Date: 2021-02-24 22:21:29
LastEditTime: 2021-02-25 22:26:55
'''
from flask import Flask,request,jsonify
import json
import dbconn
import goapi
import time
import random
import readMsg

app = Flask(__name__)
@app.route('/', methods=['POST'])
def getEvent():
    data = request.json
    post_type = data.get('post_type')
    
    if(post_type == 'message'):
        #处理消息
        message_type = data.get('message_type')
        message = data.get('message')
        user_id = str(data.get('user_id'))
        if(message_type == 'private'):
            print(f"接收消息@{user_id}:{message[:20]}")
            msg = readMsg.read(user_id,message)
            goapi.sendMsg(user_id,msg)

    elif(post_type == 'request'):
        #处理加好友请求，自动添加好友
        request_type = data.get('request_type')
        if(request_type=='friend'):
            user_id = str(data.get('user_id'))
            comment = str(data.get('comment'))
            flag = str(data.get('flag'))
            print(f"接收加好友请求@{user_id}:{comment[:20]}")
            time.sleep(random.randint(5,10))
            goapi.add_request(flag)
            time.sleep(random.randint(5,10))
            goapi.sendMsg(user_id,readMsg.user_tips)
    else:
        #防止go-cq上报错误
        pass

    return data

if __name__ == '__main__':
    app.run(host='127.0.0.1',port='5002',debug=False)
