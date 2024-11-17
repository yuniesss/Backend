from flask import Flask
from app import app
import os
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy


@app.route('/')
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
