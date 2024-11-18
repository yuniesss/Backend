from flask import Flask
from app import app
import os
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
# smtplib 用于邮件的发信动作
import smtplib
from email.mime.text import MIMEText
# email 用于构建邮件内容
from email.header import Header

@app.route('/')

def mail():
    # 发信方的信息
    from_addr = 'jingxiao_cao@126.com' # 发信信箱
    password = 'UDuLP4xLJNzTFyF5' # POP3/SMTP服务开启时的授权码

    # 收信方邮箱
    to_addr = 'jingxiao.cao@stu.pku.edu.cn'

    # 发信服务器
    smtp_server = 'smtp.126.com'

    """标题"""
    head = "邮箱验证码"
    """正文"""
    text = "【答疑平台】您的验证码是：123456，该验证码5分钟内有效，请勿泄漏于他人！"

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
    server.sendmail(from_addr, to_addr, msg.as_string())

    # 关闭服务器
    server.quit()

    return
    
def home():
    return '点击登录页面'

def validate_user(user_id, password, filename):
    # 尝试打开文件并逐行读取
    try:
        with open(filename, 'r') as file:
            for line in file:
                # 去除每行的首尾空白字符
                line = line.strip()
                # 检查行是否非空
                if line:
                    # 分割用户id和密码
                    stored_id, stored_password = line.split(':')
                    # 检查输入的用户id和密码是否匹配
                    if stored_id == user_id and stored_password == password:
                        return True
        return False
    except FileNotFoundError:
        print(f"错误：文件 {filename} 未找到。")
        return False
    except Exception as e:
        print(f"发生错误：{e}")
        return False

@app.route('/api/login',methods = ['POST'] )
def login():
    data = request.get_json()
    #处理post数据
    user_id = data['userid']
    user_password = data['userpassword']
    filename = "c:/Users/dell/Desktop/项目/app/user.txt"
    with open(filename,'r') as file:
        for line in file:
            print(line.strip())

    if validate_user(user_id, user_password, filename):
        return jsonify({"login": 1})
    else:
        return jsonify({"login": -1})
    
    #return 登录成功

@app.route('/api/signup',method = ['POST'])
def signup():
    data = request.get_json()
    user_id = data['userid']
    user_password = data['userpassword']

    # 指定文件名
    file_name = "c:/Users/dell/Desktop/项目/app/user.txt"

    # 打开文件，并追加内容
    with open(file_name, "a") as file:
        # 写入user_id和user_password，用冒号分隔，然后换行
        file.write(f"{user_id}:{user_password}\n")
    return jsonify({"signup": 1})

@app.route('/api/show',method = ['GET'])
def show():
    id = request.args.get('id')
    if id == None :
        #此处应该有一个方法
        #调数据库
        #返回一个json表单
        print('no id')
    else :
        #同上
        print('id = ????') 
    return

@app.route('/search')#需要您的研究
def search():
    return

@app.route('/mainmenu')
def mainmenu():
    return


if __name__ == '__main__':       
    app.run()
