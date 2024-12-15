#################################
#login 也要重写
#用户注册登录功能
#其中signup和confirm和数据库的交互需要重写
#################################

import random
import smtplib

from email.mime.text import MIMEText
from email.header import Header
from flask import Blueprint,request,jsonify
from datetime import datetime, timedelta

from app.models import Users
from .db import db


auth = Blueprint('auth',__name__)

def mail(email):
    # 发信方的信息
    from_addr = 'jingxiao_cao@126.com' # 发信信箱
    password = 'UDuLP4xLJNzTFyF5' # POP3/SMTP服务开启时的授权码

    # 收信方邮箱
    to_addr = email

    # 发信服务器
    smtp_server = 'smtp.126.com'

    """标题"""
    head = "邮箱验证码"
    """正文"""
    random_number = random.randint(100000, 999999)
    random_number_str = str(random_number)
    print(random_number_str)
    text = "【答疑平台】您的验证码是："+random_number_str+"，该验证码5分钟内有效，请勿泄漏于他人！"

    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
    msg = MIMEText(text, 'plain', 'utf-8')

    # 邮件头信息
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header(head)

    # 开启发信服务，这里使用的是加密传输
    # server = smtplib.SMTP_SSL()
    server = smtplib.SMTP_SSL(smtp_server)
    server.connect(smtp_server, 465)

    # 登录发信邮箱
    server.login(from_addr, password)

    # 发送邮件
    #server.sendmail(from_addr, to_addr, msg.as_string())

    # 关闭服务器
    server.quit()

    return random_number_str


@auth.route('/api/login',methods = ['POST'] )
def login():
    data = request.get_json()
    #处理post数据
    user_email = data['user_email']
    user_password = data['user_password']
    print(user_email,user_password)
    user_id = Users.login(user_email, user_password)
    
    if user_id is not None:
        return jsonify({"message": "message","login":1})
    else:
        return jsonify({'error': 'Invalid email or password',"login":0
                        }
                       )
    

@auth.route('/api/signup',methods = ['POST'])
def signup():
    data = request.get_json()
    email = data['user_email']
    user_password = data['user_password']
    username=data['username']
    given_verification_string = data['emailcheckcode']
    user_id = Users.get_user_by_email(email)
    if user_id:
        return jsonify({
            "code":400,
            "signup": -1,
            })
    input_filename = "./Backend/app/confirm.txt"
    output_filename = "./Backend/app/confirm.txt"
    # 读取文件并处理每一行
    flag = 0
    data_lines = []
    with open(input_filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # 确保不处理空行
                id, verification_string, timestamp_str = line.split(',')
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                # 检查ID和验证码
                current_time = datetime.now()
                if current_time - timestamp < timedelta(minutes=3):
                    data_lines.append(line)
                    if id == email and verification_string == given_verification_string:
                        flag = 1
    with open(output_filename, 'w') as file:
        for line in data_lines:
            file.write(line + '\n')                    

    if flag == 1:    
        new_user = Users (
            username=username,
            email=email,
            password_hash=user_password,
        )

        # 设置密码哈希
        new_user.set_password(new_user.password_hash)

        # 添加新用户到数据库会话
        db.session.add(new_user)
        print(1)
        db.session.commit()
        print(2)

        return jsonify({
                "info":"注册成功",
                "code":200,
                "signup": 1,
                })
    else:
        return jsonify({
            "info":"验证码错误",
            "code":400,
            "signup": 0,
            })
    
@auth.route('/api/changepassword',methods = ['POST'])
def changepassword():
    data = request.get_json()
    email = data['user_email']
    user_password = data['user_password']
    given_verification_string = data['emailcheckcode']
    user = Users.get_user_by_email(email)
    if user is  None:
        return jsonify({
            "code":400,
            "result": -1,
            })
    input_filename = "./Backend/app/confirm.txt"
    output_filename = "./Backend/app/confirm.txt"
    # 读取文件并处理每一行
    flag = 0
    data_lines = []
    with open(input_filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # 确保不处理空行
                id, verification_string, timestamp_str = line.split(',')
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                # 检查ID和验证码
                current_time = datetime.now()
                if current_time - timestamp < timedelta(minutes=3):
                    data_lines.append(line)
                    if id == email and verification_string == given_verification_string:
                        flag = 1
    with open(output_filename, 'w') as file:
        for line in data_lines:
            file.write(line + '\n')                    

    if flag == 1:    

        user.password_hash=user_password
        # 设置密码哈希
        user.set_password(user.password_hash)

        # 添加用户到数据库会话
        db.session.commit()
        print(2)

        return jsonify({
                "info":"更改成功",
                "code":200,
                "result": 1,
                })
    else:
        return jsonify({
            "info":"验证码错误",
            "code":400,
            "result": 0,
            })
    

@auth.route('/api/confirm',methods = ['POST'])
def confirm():
    data = request.get_json()
    given_id = data['userid']
    user = Users.get_user_by_email(given_id)
    if user is  None:
        return jsonify({
            "code":400,
            "confirm": -1,
            })
    ret = mail(given_id)
    verification_string = ret
    # 获取当前时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"{given_id},{verification_string},{timestamp}\n"
    # 写入文件
    with open("./Backend/app/confirm.txt", 'a') as file:
        file.write(content)

    return jsonify({"confirm":1})


