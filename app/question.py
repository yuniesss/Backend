#################################
#问题功能
#处理问题，回答的创建，查询，更改
#推送功能，可能要拆出来和搜索一起
#################################

from flask import request,Blueprint,jsonify

from .models import Questions,Answers,Users
from .db import db

question = Blueprint('question',__name__)


#用户登录后首页给他推送10个问题
@question.route('/api/pushlist', methods=['POST']) 
def push_list():
    data = request.get_json()
    questions = Questions.query.order_by(Questions.created_at.desc()).limit(10).all()
    latest_questions_list = [{'id': q.id, 'title': q.title, 'body': q.body, 'created_at': q.created_at} for q in questions]
    return jsonify({
        "code":200,
        "list":latest_questions_list,
        }
        )

#前端创建了一个问题，请更改数据库
@question.route('/api/createquestion', methods=['POST'])
def createquestion():
    data = request.get_json()
    title=data['title']
    body=data['body']
    email=data['email']
    existing_user = Users.query.filter_by(email=email).first()
    new_q = Questions (
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


#前端建立了一个回答，更改数据库
@question.route('/api/createanswer', methods=['POST'])
def createanswer():
    data = request.get_json()
    body=data['body']
    email=data['email']
    questionid=data['questionid']
    existing_user = Users.query.filter_by(email=email).first()
    new_a = Answers (
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


#前端传入一个id，返回一个问题的内容
@question.route('/api/getuserquestion', methods=['POST'])
def getuserquestion():
    data = request.get_json()
    email = data.get('email')
    existing_user = Users.query.filter_by(email=email).first()
    
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


#前端传入一个问题id，返回这个问题全部回答的内容
@question.route('/api/getanswer', methods=['POST'])
def getanswer():
    data = request.get_json()
    question_id = data.get('questionid')
    question= Questions.query.get(question_id)
    
    if question is None:
        return jsonify({"code": 404, "message": "Question not found"})
    answers_list = [{'id': a.id, 'body': a.body, 'created_at': a.created_at,'author': a.author.username,"likes":0} for a in question.answers]
    print(answers_list)
    return jsonify({
        "code":200,
        "answers": answers_list
        }
        )
