from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import pandas as pd
import numpy as np
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:wh13213682290@forgd'
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
db = SQLAlchemy(app)


# 0数据库链接测试
def db_test():
    dict_show = {}  # 定义字典用于数据展示
    # 反射数据库中已存在的表，并获取所有存在的表对象。
    db.reflect()
    # 获取所有表名
    all_table = {table_obj.name: table_obj for table_obj in db.get_tables_for_bind()}
    # 获取demo表的所有数据
    all_data = db.session.query(all_table['demo'])
    for data in all_data:
        print(data)  # 查看数据
        dict_show[data[0]] = [data[1], data[2]]
    return jsonify(dict_show)

#编号生成
def fororderID(number):
    numbers = eval(number)
    if numbers <= 50:
        N =  "S"
    elif numbers > 50 and numbers <= 150:
        N = "M"
    elif numbers > 150:
        N = "L"

    year = datetime.datetime.today().year
    month = datetime.datetime.today().month
    day = datetime.datetime.today().day
    hour = datetime.datetime.today().hour
    minute = datetime.datetime.today().minute
    second = datetime.datetime.today().second
    OrderID = '%s%s%s%s%s%s%s'%(N,year,month,day,hour,minute,second)
    print(OrderID)
    return OrderID

def UrgentCount(ReceiveTime, Number, Deadline):
    # 计算已经过去的时间
    now = datetime.datetime.now()
    ReceiveTime = pd.to_datetime(ReceiveTime)
    LastTime = (now - ReceiveTime).days
    # 计算剩余时间
    Deadline = pd.to_datetime(Deadline)
    RemainTime = (Deadline - now).days
    Number = eval(Number)
    # 计算订单数量权重
    num_weights = {'50-100': 0.3, '100-200': 0.6, '200-300': 0.9}
    if Number < 50:
        num_weight = num_weights['50-100']
    elif Number >= 50 and Number < 100:
        num_weight = num_weights['50-100'] + (num_weights['100-200'] - num_weights['50-100']) * (Number - 50) / 50
    elif Number >= 100 and Number < 200:
        num_weight = num_weights['100-200'] + (num_weights['200-300'] - num_weights['100-200']) * (Number - 100) / 100
    else:
        num_weight = num_weights['200-300']
    # 计算提交期限权重
    time_weights = {'7-15': 0.9, '15-22': 0.6, '22-30': 0.3}
    if RemainTime <= 7:
        time_weight = time_weights['7-15']
    elif RemainTime > 7 and RemainTime <= 15:
        time_weight = time_weights['7-15'] + (time_weights['15-22'] - time_weights['7-15']) * (RemainTime - 7) / 8
    elif RemainTime > 15 and RemainTime <= 22:
        time_weight = time_weights['15-22'] + (time_weights['22-30'] - time_weights['15-22']) * (RemainTime - 15) / 7
    else:
        time_weight = time_weights['22-30']
    # 计算最终权重
    final_weight = 0.6 * num_weight + 0.4 * time_weight
    # 根据权重计算优先级别
    if final_weight >= 0.8:
        priority = 4
    elif final_weight >= 0.6:
        priority = 3
    elif final_weight >= 0.4:
        priority = 2
    else:
        priority = 1

    return priority

def oneUrgent():
    return  0