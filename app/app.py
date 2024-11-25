from flask import Flask
from datetime import datetime, timedelta
import random
import os
#from app import creat_app
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
# smtplib 用于邮件的发信动作
import smtplib
from email.mime.text import MIMEText
# email 用于构建邮件内容
from email.header import Header


app = Flask(__name__)

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
    server.sendmail(from_addr, to_addr, msg.as_string())

    # 关闭服务器
    server.quit()

    return random_number_str
    
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
    filename = "./user.txt"
    with open(filename,'r') as file:
        for line in file:
            print(line.strip())

    if validate_user(user_id, user_password, filename):
        return jsonify({"login": 1})
    else:
        return jsonify({"login": -1})
    
    #return 登录成功



@app.route('/api/signup',methods = ['POST'])
def signup():
    data = request.get_json()
    given_id = data['userid']
    user_password = data['userpassword']
    given_verification_string = data['emailcheckcode']
    # 读取和处理文件
    input_filename = "C:/Users/dell/Desktop/项目/app/confirm.txt"
    output_filename = "C:/Users/dell/Desktop/项目/app/confirm.txt"
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
                    if id == given_id and verification_string == given_verification_string:
                        flag = 1

    # 将未删除的行写回文件
    with open(output_filename, 'w') as file:
        for line in data_lines:
            file.write(line + '\n')

    if flag == 1:
        file_name = "C:/Users/dell/Desktop/项目/app/user.txt"
        # 打开文件，并追加内容
        with open(file_name, "a") as file:
            # 写入user_id和user_password，用冒号分隔，然后换行
            file.write(f"\n{given_id}:{user_password}")
        return jsonify({"signup": 1})
    else:
        return jsonify({"signup":-1})
    
    # 指定文件名
    

@app.route('/api/confirm',methods = ['POST'])
def confirm():
    data = request.get_json()
    given_id = data['userid']
    ret = mail(given_id)
    verification_string = ret
    # 获取当前时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"{given_id},{verification_string},{timestamp}\n"
    # 写入文件
    with open("C:/Users/dell/Desktop/项目/app/confirm.txt", 'a') as file:
        file.write(content)

    return jsonify({"confirm":1})

@app.route('/')
def trial():
    return "hello world"

@app.route('/api/pushlist', methods=['POST']) # 【待访问数据库】用户登录后首页给他推送10个问题
def push_list():
    data = request.get_json()
    user_id = data.get('userid')  # userid的用处？实现精确推送？？
    questions_list = random.sample(list(questions_db.keys()), 10)  # 先从数据库里随机选取10个吧
    return jsonify({'question_ids': questions_list})

def check_user_interactions(question_id, user_id): # 【待访问数据库】判断用户对该问题的交互情况：是否点赞/收藏过
    # 从数据库调用，先模拟一个
    is_liked = True
    is_favorited = False
    return is_liked, is_favorited

# 【待访问数据库】 问题数据库（模拟一个）
questions_db = {
    '00001': {
        'id': '00001',
        'title': 'Is cachelab difficult?',
        'content': 'A little.',
        'like': 0,
        'favorite': 0
    },
    '00002': {
        'id': '00002',
        'title': 'Is tshlab difficult?',
        'content': 'Have some.',
        'like': 10,
        'favorite': 1
    },
    '00003': {
        'id': '00003',
        'title': 'Is malloclab difficult?',
        'content': 'Very difficult!',
        'like': 100,
        'favorite': 10
    }
}
@app.route('/api/getQuestion', methods=['POST']) # 查询问题，返回问题条目
def get_question():
    data = request.get_json()
    question_id = data.get('questionid')
    user_id = data.get('userid')

    if question_id in questions_db:
        question_data = questions_db[question_id]
        is_liked, is_favorited = check_user_interactions(question_id, user_id)

        response = {
            'id': question_data['id'],
            'title': question_data['title'],
            'content': question_data['content'],
            'like': question_data['like'],
            'favorite': question_data['favorite'],
            'isliked': is_liked,
            'isfavorited': is_favorited
        }
        return jsonify(response)
    else:
        return jsonify({'error': 'Question not found'}), 404

# 【待访问数据库】 问题的回答数据库（模拟一个）
answers_db = {
    '00003': [
        {'answer_id': 'a001', 'content': '暂时不能'},
        {'answer_id': 'a002', 'content': '给你明确的'},
        {'answer_id': 'a003', 'content': '答复'}
    ]
}

questions_list = ['123456', '234567', '345678', '456789', '567890', '678901', '789012', '890123', '901234', '012345']

@app.route('/api/getAnswer', methods=['POST']) # 查询问题对应的回答，返回回答列表
def get_answer():
    data = request.get_json()
    question_id = data.get('questionid')

    if question_id in answers_db:
        answers = answers_db[question_id]
        return jsonify(answers)
    else:
        return jsonify({'error': 'No answers found for this question'}), 404

@app.route('/api/get', methods=['POST']) # 查询回答，返回回答条目
def get_answer_detail():
    data = request.get_json()
    question_id = data.get('questionid')
    answer_id = data.get('answerid')
    # 检查问题ID是否存在
    if question_id in answers_db:
        # 在问题的回答中查找指定的回答 ID
        for answer in answers_db[question_id]:
            if answer['answer_id'] == answer_id:
                return jsonify(answer)
        return jsonify({'error': 'Answer ID not found in the provided Question ID'}), 404
    else:
        return jsonify({'error': 'Question ID not found'}), 404

###########################################################################################


@app.route('/api/show',methods = ['GET'])
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
    
