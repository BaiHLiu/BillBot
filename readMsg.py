'''
Descripttion: 
version: 
Author: Catop
Date: 2021-02-24 22:47:12
LastEditTime: 2021-03-13 00:29:26
'''
import time
import datetime
import dbconn
from datetime import timedelta



user_tips = "欢迎使用记账机器人!功能及使用方法:\n⚡本周账单/统计\n⚡本月账单/统计\n⚡指定月份账单/统计(例如'1月统计')\n⚡指定日期范围账单/统计(例如'指定日期账单@2021-01-23@2021-03-09')\n⚡最近(将查询最近10条交易记录)\n⚡删除(需要先通过最近记录查到pid，如pid为102,则使用'删除 102'\n"
user_tips += "⚡记账功能：回复'名称 金额'即可快捷记账。比如'奶茶 12',中间有空格\n"
user_tips += "\n常见问题FAQ:\n"
user_tips += "1.我的数据存储安全吗？\n答：并不安全，在数据库中使用明文存储。但是，由于qq机器人交互的局限性，菜鸟我当前没有想出合理高效的加密方法，但我承诺不会随意读取数据库中内容。因此，除非遇到设备被盗、黑客攻击，您的账单永远不会被泄露。\n\n"
user_tips += "2.忘记指令怎么办？\n答：回复'帮助'可获得帮助信息。\n\n"
user_tips += "3.统计功能如何分类？\n答：目前机器人只有简单的记账，并不能自动分类。因此，建议您自己约定合适的分类方法，如 就餐、聚餐、学习、零食、美妆、基础物资、电子、生活、娱乐"



def read(user_id,message):
    try:
        msg = ""
        if('帮助' in message):
            return user_tips
        if('本周' in message):
            if('账单' in message):
                msg = get_week_details(user_id)
            elif('统计' in message):
                msg = get_week_details(user_id,stt=1)
        elif('本月' in message):
            if('账单' in message):
                msg = get_month_details(user_id)
            elif('统计' in message):
                msg = get_month_details(user_id,month=0,stt=1)
        elif('月' in message):
            month_str_end = 0
            month_str_start = 0
            for i in range(0,len(message)):
                if(message[i] == '月'):
                    month_str_end = i #月份数字结束位置
                    break
                i += 1
            for i in range(0,month_str_end):
                if(ord(message[i])>=48 and ord(message[i])<=57):
                    month_str_start = i #月份数字开始位置
                    break
                i += 1
            if('账单' in message):
                msg = get_month_details(user_id,message[month_str_start:month_str_end])
            elif('统计' in message):
                msg = get_month_details(user_id,message[month_str_start:month_str_end],stt=1)

        elif('指定日期' in message):
            start_time = message.split('@')[1]
            end_time = message.split('@')[2]
            if('账单' in message):
                msg = get_specific_details(user_id,start_time,end_time)
            else:
                msg = get_specific_details(user_id,start_time,end_time,stt=1)
        elif('最近' in message):
            msg = recent_bill(user_id)
        elif('删除' in message):
            pid = message.split(' ')[1]
            msg = del_bill(user_id,pid)
        else:
            #新增记录
            bill_name = message.split(' ')[0]
            bill_amount = message.split(' ')[1]
            msg = new_bill(user_id,bill_name,bill_amount)
            
        return msg

    except:
        msg = "输入有误，请回复'帮助'获取帮助信息"
        return msg
    else:
        print(f"成功处理用户{user_id}")

    
        
"""
stt(statistics):
0 = 详情模式
1 = 统计模式
"""

            
def get_week_details(user_id,stt=0):
    """获取本周账单"""
    start_time = str(get_current_week()[0])+" 00:00:00"
    end_time = str(get_current_week()[1])+" 00:00:00"
    bill_list = dbconn.get_bill(user_id,start_time,end_time)

    #获取上周金额
    last_start_time = str(get_current_week()[0] - timedelta(weeks=1))+" 00:00:00"
    last_end_time = str(get_current_week()[1] - timedelta(weeks=1))+" 00:00:00"
    last_bill_list = dbconn.get_bill(user_id,last_start_time,last_end_time)
    last_amount_sum = 0
    for i in range(0,len(last_bill_list)):
        last_amount_sum += last_bill_list[i]['bill_amount']

    
    if(stt==0):
        msg = f"----本周账单详情----\n{get_current_week()[0]}~{get_current_week()[1]}\n"
        amount_sum = 0
        for i in range(0,len(bill_list)):
            msg += f"⚡ {i}:{bill_list[i]['bill_name']}￥{bill_list[i]['bill_amount']}\n{bill_list[i]['bill_time']}\n"
            amount_sum += bill_list[i]['bill_amount']
        amount_sum = ('%.2f'%amount_sum)
        msg += f"共计{len(bill_list)}笔消费，共{amount_sum}元。"
        #计算本周占上周比例
        if(float(last_amount_sum)>0):
            last_amount_sum = ('%.2f'%last_amount_sum)
            last_ratio = (('%.2f')%(float(amount_sum)/float(last_amount_sum)*100))
            ratio_msg = f"\n上周消费共计{last_amount_sum}元，已占{last_ratio}%"
            msg += ratio_msg

            last_week_ratio_msg = ratio_msg
    else:
        msg = get_stt(user_id,start_time,end_time,bill_list)



    return msg




def get_current_week():
    """获取当周开始和结束日期"""
    monday, sunday = datetime.date.today(), datetime.date.today()
    one_day = datetime.timedelta(days=1)
    while (monday.weekday() != 0):
        monday -= one_day
    while (sunday.weekday() != 6):
        sunday += one_day
	
    return monday, sunday


def get_month_details(user_id,month=0,stt=0):
    year_month = str(time.strftime("%Y-%m", time.localtime()))
    year = str(time.strftime("%Y", time.localtime()))
    if(month == 0):
        """即当月账单"""
        start_time = year_month+"-01"+" 00:00:00"
        end_time = year_month+"-31"+" 00:00:00"
        month = datetime.date.today().month
    else:
        start_time = year+f"-{month}-01"+" 00:00:00"
        end_time = year+f"-{month}-31"+" 00:00:00"
        
    bill_list = dbconn.get_bill(user_id,start_time,end_time)

    if(stt==0):
        msg = f"----本月账单详情----\n{year}年-{month}月\n"
        amount_sum = 0
        for i in range(0,len(bill_list)):
            msg += f"⚡ {i}:{bill_list[i]['bill_name']}￥{bill_list[i]['bill_amount']}\n{bill_list[i]['bill_time']}\n"
            amount_sum += bill_list[i]['bill_amount']
        amount_sum = ('%.2f'%amount_sum)
        msg += f"共计{len(bill_list)}笔消费，共{amount_sum}元。"

        #获取上月金额，防止1月报错
        last_start_time = year+f"-{int(month)-1}-01"+" 00:00:00"
        last_end_time = year+f"-{int(month)-1}-31"+" 00:00:00"
        last_bill_list = dbconn.get_bill(user_id,last_start_time,last_end_time)
        last_amount_sum = 0
        for i in range(0,len(last_bill_list)):
            last_amount_sum += last_bill_list[i]['bill_amount']
        last_amount_sum = ('%.2f'%last_amount_sum)
        if(float(last_amount_sum) > 0):
            last_ratio = (('%.2f')%(float(amount_sum)/float(last_amount_sum)))
            msg += f"\n上月消费共计{last_amount_sum}元，已占{float(last_ratio)*100}%"
    else:
        msg = get_stt(user_id,start_time,end_time,bill_list)

    return msg
    
def get_specific_details(user_id,start_time,end_time,stt=0):
    """获取指定日期内账单"""
    msg = f"----指定日期账单----\n{start_time}~{end_time}\n"
    start_time += " 00:00:00"
    end_time += " 00:00:00"
    bill_list = dbconn.get_bill(user_id,start_time,end_time)

    if(stt==0):
        amount_sum = 0
        for i in range(0,len(bill_list)):
            msg += f"⚡ {i}:{bill_list[i]['bill_name']}￥{bill_list[i]['bill_amount']}\n{bill_list[i]['bill_time']}\n"
            amount_sum += bill_list[i]['bill_amount']
        amount_sum = ('%.2f'%amount_sum)
        msg += f"共计{len(bill_list)}笔消费，共{amount_sum}元。"
    else:
        msg = get_stt(user_id,start_time,end_time,bill_list)

    return msg
    
def get_stt(user_id,start_time,end_time,bill_list):
    """整理统计信息"""
    msg = f"----消费统计----\n{start_time.split(' ')[0]}~{end_time.split(' ')[0]}\n"
    amount_sum = 0
    stt_dict = {}
    for i in range(0,len(bill_list)):
        if not (bill_list[i]['bill_name'] in stt_dict.keys()):
            stt_dict[bill_list[i]['bill_name']] = float(bill_list[i]['bill_amount'])
        else:
            stt_dict[bill_list[i]['bill_name']] += float(bill_list[i]['bill_amount'])
        amount_sum += bill_list[i]['bill_amount']
    amount_sum = ('%.2f'%amount_sum)
    for bill_name in stt_dict.keys():
        if(float(amount_sum) > 0):
            ratio = (('%.2f')%(float(stt_dict[bill_name])/float(amount_sum)*100))
        else:
            ratio = '0'
        stt_dict[bill_name] = ('%.2f'%stt_dict[bill_name])
        msg += f"⚡ {bill_name}:￥{stt_dict[bill_name]} ({ratio}%)\n"
    msg += f"共计{len(bill_list)}笔消费，共{amount_sum}元。"
    
    
    #获取上周金额
    last_start_time = str(get_current_week()[0] - timedelta(weeks=1))+" 00:00:00"
    last_end_time = str(get_current_week()[1] - timedelta(weeks=1))+" 00:00:00"
    last_bill_list = dbconn.get_bill(user_id,last_start_time,last_end_time)
    last_amount_sum = 0
    for i in range(0,len(last_bill_list)):
        last_amount_sum += last_bill_list[i]['bill_amount']
        
    #计算本周占上周比例
    if(float(last_amount_sum)>0):
        last_amount_sum = ('%.2f'%last_amount_sum)
        last_ratio = (('%.2f')%(float(amount_sum)/float(last_amount_sum)*100))
        ratio_msg = f"\n上周消费共计{last_amount_sum}元，已占{last_ratio}%"
        msg += ratio_msg

    return msg

def new_bill(user_id,bill_name,bill_amount):
    dbconn.add_bill(user_id,bill_name,bill_amount)
    today_start_time = str(time.strftime("%Y-%m-%d", time.localtime())) + " 00:00:00"
    today_end_time = str(time.strftime("%Y-%m-%d", time.localtime())) + " 24:00:00"
    today_bill = dbconn.get_bill(user_id,today_start_time,today_end_time)
    
    today_amount = 0
    today_count = len(today_bill)
    
    for i in range(0,len(today_bill)):
        today_amount += today_bill[i]['bill_amount']

    today_amount = ('%.2f'%today_amount)
    sum_amount = dbconn.get_sum(user_id)[0]
    sum_count = dbconn.get_sum(user_id)[1]
    if(int(sum_count) > 0):
        avg = float(sum_amount)/int(sum_count)
        avg = ('%.2f'%avg)
    else:
        avg = 0
    msg = f"⚡ 记账成功\n{bill_name}:￥{bill_amount}\n\n今天共计{today_count}笔消费，总计{today_amount}元\n每天平均:￥{avg}\n这是陪你的第{sum_count}个日子"

    return msg

def recent_bill(user_id):
    bill_list = dbconn.get_recent(user_id)
    amount_sum = 0
    msg = "----最近10笔消费----\n"
    for i in range(0,len(bill_list)):
        msg += f"⚡ pid={bill_list[i]['id']}:{bill_list[i]['bill_name']}￥{bill_list[i]['bill_amount']}\n{bill_list[i]['bill_time']}\n"
        amount_sum += bill_list[i]['bill_amount']
    amount_sum = ('%.2f'%amount_sum)
    msg += f"共计{len(bill_list)}笔消费，共{amount_sum}元。"

    return msg

def del_bill(user_id,pid):
    dbconn.del_bill(pid,user_id)
    msg = f"已尝试删除PaymendID={pid}的账单"

    return msg

if __name__ == '__main__':
    #print(get_current_week())
    #read('601179193','本周账单')
    #print(get_month_details('601179193'))
    #print(read('601179193','本周账单'))
    #print(get_specific_details('601179193','2021-2-3','2021-2-27'))    
    #read('601179193','2月账单')
    #print(get_month_details('601179193',month=2,stt=1))
    #print(new_bill('601179193','工具1','18.01'))
    #print(recent_bill('601179193'))
    #print(del_bill('601179193','12'))
    print(new_bill('601179193','测试新账单2','7.12'))