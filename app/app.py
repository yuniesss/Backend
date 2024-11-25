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



app = Flask(__name__)
app.config.from_object('config.settings')
db = SQLAlchemy(app)







# 问题表
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)  # 问题ID
    title = db.Column(db.String(255), nullable=False)  # 问题标题
    body = db.Column(db.Text, nullable=False)  # 问题内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 提问时间
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 提问者的ID


    # 与回答表的关系：一个问题可以有多个回答
    answers = db.relationship('Answer', backref='question', lazy=True)

    def __repr__(self):
        return f"<Question(id={self.id}, title={self.title}, created_at={self.created_at})>"



# 回答表
class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)  # 回答ID
    body = db.Column(db.Text, nullable=False)  # 回答内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 回答时间
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)  # 所属问题ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 回答者的ID
    

    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, created_at={self.created_at})>"
# 用户表
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # 用户ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱
    password_hash = db.Column(db.String(256), nullable=False)  # 密码哈希
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间
    
    # 与 Question 表的关系：一个用户可以提多个问题
    questions = db.relationship('Question', backref='author', lazy=True)

    # 与 Answer 表的关系：一个用户可以回答多个问题
    answers = db.relationship('Answer', backref='author', lazy=True)

    def set_password(self, password):
        """ 设置密码的哈希值 """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ 检查密码是否匹配 """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"




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

@app.route('/api/signup',methods = ['POST'])
def signup():
    data = request.get_json()
    email = data['userid']
    user_password = data['userpassword']
    given_verification_string = data['emailcheckcode']
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
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

@app.route('/')
def trial():
    return "hello world"

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
@app.route('/api/pushlist', methods=['POST']) # 【待访问数据库】用户登录后首页给他推送10个问题
def push_list():
    data = request.get_json()
    questions = Question.query.order_by(Question.created_at.desc()).limit(10).all()
    latest_questions_list = [{'id': q.id, 'title': q.title, 'body': q.body, 'created_at': q.created_at} for q in questions]
    return jsonify({
        "code":200,
        "list":latest_questions_list,
        }
        )
@app.route('/api/getquestion', methods=['POST'])
def getquestion():
    data = request.get_json()
    question_id = data.get('questionid')
    q= Question.query.filter_by(id=question_id).first()
    question={'id': q.id, 'title': q.title, 'body': q.body, 'created_at': q.created_at}
    return jsonify({
        "code":200,
        "question":question,
        }
        )
@app.route('/api/getuserquestion', methods=['POST'])
def getuserquestion():
    data = request.get_json()
    email = data.get('email')
    existing_user = User.query.filter_by(email=email).first()
    
    questions_list = [{
        'id': q.id,
        'title': q.title,
        'body': q.body,
        'created_at': q.created_at.isoformat()
    } for q in existing_user.questions]
    
    return jsonify({
        "code":200,
        "questions":questions_list,
        }
        )

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

@app.route('/api/getanswer', methods=['POST'])
def getanswer():
    data = request.get_json()
    question_id = data.get('questionid')
    question= Question.query.get(question_id)
    
    if question is None:
        return jsonify({"code": 404, "message": "Question not found"})
    answers_list = [{'id': a.id, 'body': a.body, 'created_at': a.created_at,'author': a.author.username,"likes":0} for a in question.answers]
    print(answers_list)
    return jsonify({
        "code":200,
        "answers": answers_list
        }
        )

def check_user_interactions(question_id, user_id): # 【待访问数据库】判断用户对该问题的交互情况：是否点赞/收藏过
    # 从数据库调用，先模拟一个
    is_liked = True
    is_favorited = False
    return is_liked, is_favorited




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

with app.app_context():
    db.create_all()

if __name__ == '__main__':       
    app.run()

