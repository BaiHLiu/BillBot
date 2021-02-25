'''
Descripttion: 
version: 
Author: Catop
Date: 2021-02-24 22:20:14
LastEditTime: 2021-02-25 21:30:33
'''

import pymysql
import time
from datetime import datetime
conn = pymysql.connect(host='192.168.123.180',user = "billbot",passwd = "6iBsTjMn2xJmk6FF",db = "billbot")


current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def add_bill(user_id,bill_name,bill_amount):
    """新增记录"""
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    params = [bill_name,bill_amount,current_time,user_id]
    sql = "INSERT INTO BB_flow(bill_name,bill_amount,bill_time,user_id) VALUES (%s,%s,%s,%s)"
    conn.ping(reconnect=True)
    cursor.execute(sql,params)
    conn.commit()

    return cursor.lastrowid

def del_bill(bill_id,user_id):
    """删除记录"""
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    params = [bill_id,user_id]
    sql = "DELETE FROM BB_flow WHERE (id=%s AND user_id=%s) LIMIT 1"
    conn.ping(reconnect=True)
    cursor.execute(sql,params)
    conn.commit()

    return cursor.lastrowid


def get_bill(user_id,time_start,time_end):
    """获取指定时间段内用户账单"""
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    params = [time_start,time_end,user_id]
    sql = "SELECT * FROM BB_flow WHERE(bill_time>=%s AND bill_time<=%s AND user_id=%s) ORDER BY bill_time"
    conn.ping(reconnect=True)
    cursor.execute(sql,params)
    conn.commit()
    bill_list = cursor.fetchall()

    return bill_list

def get_sum(user_id):
    """获取用户所有账单总金额和使用天数"""
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    params = [user_id]
    sql = "SELECT * FROM BB_flow WHERE(user_id=%s) ORDER BY bill_time"
    conn.ping(reconnect=True)
    cursor.execute(sql,params)
    conn.commit()
    bill_list = cursor.fetchall()

    sum_amount = 0
    now_time = datetime.today()
    #print(bill_list[0]['bill_time'])
    #print(now_time)
    sum_count = (now_time - bill_list[0]['bill_time']).days
    for i in range(0,len(bill_list)):
        sum_amount += bill_list[i]['bill_amount']
    sum_amount = ('%.2f'%sum_amount)

    return sum_amount,sum_count

def get_recent(user_id):
    """获取最近10条消费记录"""
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    params = [user_id]
    sql = "SELECT * FROM BB_flow WHERE(user_id=%s) ORDER BY id LIMIT 10"
    conn.ping(reconnect=True)
    cursor.execute(sql,params)
    conn.commit()
    bill_list = cursor.fetchall()

    return bill_list

if __name__ == '__main__':
    #add_bill('601179193','测试消费','12.0872')
    #print(del_bill('8','601179194'))
    #print(get_bill('601179193','2021-02-25 00:00:00','2021-02-25 09:00:00'))
    print(get_sum('601179193'))
    #print(get_recent('601179193'))
