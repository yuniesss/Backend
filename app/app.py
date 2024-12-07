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
#数据库相关
from config import settings
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app_init import app,db
from models import User,Team,TeamMembership,Question,Answer,QuestionLike,AnswerLike

# 为注册用户发送邮箱验证码
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
    
# 查询用户是否注册
@app.route('/api/getusername',methods = ['POST'] )
def getusername():
    data = request.get_json()
    email = data['userid']
    user_password = data['userpassword']
    existing_user = User.query.filter_by(email=email).first()

    if existing_user.check_password(user_password):
        return jsonify(
            {
            "info":"查询成功",
            "code":200,
            "username":  existing_user.username
            })
    else:
        return jsonify(
            {
            "info":"查询失败",
            "code":400,
            "username": '',
            })

# 修改用户名
@app.route('/api/changeusername',methods = ['POST'] )
def changeusername():
    data = request.get_json()
    username=data['username']
    email = data['userid']
    user_password = data['userpassword']
    existing_user = User.query.filter_by(email=email).first()

    if existing_user.check_password(user_password):
        existing_user.username=username
        db.session.commit()
        return jsonify(
            {
            "info":"修改成功",
            "code":200,
            "username": username,
            })
    else:
        return jsonify(
            {
            "info":"修改失败",
            "code":400,
            "username": username,
            
            })

# 登录
@app.route('/api/login',methods = ['POST'] )
def login():
    data = request.get_json()
    #处理post数据
    email = data['email']
    user_password = data['userpassword']
    existing_user = User.query.filter_by(email=email).first()
    
    if existing_user.check_password(user_password):
        return jsonify({"login": 1})
    else:
        return jsonify({"login": -1})

# 注册
@app.route('/api/signup',methods = ['POST'])
def signup():
    data = request.get_json()
    email = data['userid']
    user_password = data['userpassword']
    given_verification_string = data['emailcheckcode']
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "info": "该邮箱已注册",
            "code":400,
            "signup": -1,
            })
        
    new_user = User (
        username=email,
        email=email,
        password_hash=user_password,
    )

    # 设置密码哈希
    new_user.set_password(new_user.password_hash)

    # 添加新用户到数据库会话
    db.session.add(new_user)

    # 提交会话以保存到数据库
    try:
        db.session.commit()
        return jsonify({
            "info":"注册成功",
            "code":200,
            "signup": 1,
            })
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "info":"插入失败，可能有重复",
            "code":400,
            "signup": -1,
            })
    except Exception as e:
        db.session.rollback()
        return f'数据库错误: {str(e)}', 500
    
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
    with open("./hou/Backend/app/confirm.txt", 'a') as file:
        file.write(content)

    return jsonify({"confirm":1})


# 创建问题
@app.route('/api/createquestion', methods=['POST'])
def createquestion():
    data = request.get_json()
    title=data['title']
    body=data['body']
    email=data['email']
    existing_user = User.query.filter_by(email=email).first()

    new_q = Question (
        title=title,
        body=body,
        user_id=existing_user.id
    )

    db.session.add(new_q)
    db.session.commit()

    return jsonify({
        "code":200,
        }
        )

# 用户登录后推送
@app.route('/api/pushlist', methods=['POST'])
def push_list():
    data = request.get_json()
    questions = Question.query.order_by(Question.created_at.desc()).limit(10).all()

    latest_questions_list = [{'id': q.id,
                              'title': q.title,
                              'body': q.body,
                              'created_at': q.created_at
                              } for q in questions]

    return jsonify({
        "code":200,
        "list":latest_questions_list,
        }
        )

# 获取问题详情
@app.route('/api/getquestion', methods=['POST'])
def getquestion():
    data = request.get_json()
    question_id = data.get('questionid')
    q= Question.query.filter_by(id=question_id).first()

    question={'id': q.id,
              'title': q.title,
              'body': q.body,
              'created_at': q.created_at,
              'likes': q.likes.count()
              }

    return jsonify({
        "code":200,
        "question":question,
        }
        )

# 查询用户所有问题
@app.route('/api/getuserquestion', methods=['POST'])
def getuserquestion():
    data = request.get_json()
    email = data.get('email')
    existing_user = User.query.filter_by(email=email).first()
    
    questions_list = [{
        'id': q.id,
        'title': q.title,
        'body': q.body,
        'created_at': q.created_at.isoformat(),
        'likes': q.likes.count()
    } for q in existing_user.questions]
    
    return jsonify({
        "code":200,
        "questions":questions_list,
        }
        )

# 创建回答
@app.route('/api/createanswer', methods=['POST'])
def createanswer():
    data = request.get_json()
    body=data['body']
    email=data['email']
    questionid=data['questionid']
    existing_user = User.query.filter_by(email=email).first()

    new_a = Answer (
        body=body,
        user_id=existing_user.id,
        question_id=questionid
    )
    db.session.add(new_a)
    db.session.commit()

    return jsonify({
        "code":200,
        }
        )

# 查询问题的所有回答
@app.route('/api/getanswer', methods=['POST'])
def getanswer():
    data = request.get_json()
    question_id = data.get('questionid')
    question= Question.query.get(question_id)
    
    if question is None:
        return jsonify({"code": 404, "message": "Question not found"})

    answers_list = [{
        'id': a.id,
        'body': a.body,
        'created_at': a.created_at,
        'author': a.author.username,
        "likes": a.likes.count()
    } for a in question.answers]

    print(answers_list)
    return jsonify({
        "code":200,
        "answers": answers_list
        }
        )


# 对问题点赞
@app.route('/api/likequestion', methods=['POST'])
def like_question():
    # 前端返回用户email，问题id
    data = request.get_json()
    question_id = data['question_id']
    email = data['email']

    user = User.query.filter_by(email=email).first() # 查找用户，核实是否为合法用户
    if not user:
        return jsonify({"code": 404, "message": "User not found"})

    question = Question.query.get(question_id) # 查找问题，核实问题是否存在
    if not question:
        return jsonify({"code": 404, "message": "Question not found"})

    existing_like = QuestionLike.query.filter_by(user_id=user.id, question_id=question_id).first() # 该用户是否已对该问题点赞
    if existing_like:
        return jsonify({"code": 400, "message": "Already liked"})

    like = QuestionLike(user_id=user.id, question_id=question_id) # 创建新点赞
    db.session.add(like) # 将新点赞对象添加到会话中
    db.session.commit() # 提交事务，将更改保存到数据库

    return jsonify({"code": 200, "message": "Liked successfully"})

# 对回答点赞
@app.route('/api/likeanswer', methods=['POST'])
def like_answer():
    # 前端返回用户email，回答id
    data = request.get_json()
    answer_id = data['answer_id']
    email = data['email']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"code": 404, "message": "User not found"})

    answer = Answer.query.get(answer_id)
    if not answer:
        return jsonify({"code": 404, "message": "Answer not found"})

    existing_like = AnswerLike.query.filter_by(user_id=user.id, answer_id=answer_id).first()
    if existing_like:
        return jsonify({"code": 400, "message": "Already liked"})

    like = AnswerLike(user_id=user.id, answer_id=answer_id)
    db.session.add(like)
    db.session.commit()

    return jsonify({"code": 200, "message": "Liked successfully"})

if __name__ == '__main__':       
    app.run()

