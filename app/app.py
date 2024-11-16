from flask import Flask
from flask import request
import os

app = Flask(__name__)

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
                    stored_id, stored_password = line.split('：')
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

@app.route('/login',methods = ['POST'] )
def login():
    data = request.get_json()
    #这里渲染登录页面
    #处理post数据
    #

    input_id = data[id]
    input_password = data[password]
    filename = "user.txt"
    if validate_user(input_id, input_password, filename):
        return "验证成功！"
    else:
        return "验证失败：用户ID或密码错误。"
    
    #return 登录成功

@app.route('/signup')
def signup():
    user_id = "your_user_id"
    user_password = "your_password"

    # 指定文件名
    file_name = "user.txt"

    # 打开文件，并追加内容
    with open(file_name, "a") as file:
        # 写入user_id和user_password，用冒号分隔，然后换行
        file.write(f"{user_id}: {user_password}\n")
    return "成功！"


if __name__ == '__main__':

    app.run()
