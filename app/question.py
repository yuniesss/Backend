#################################
#问题功能
#处理问题，回答的创建，查询，更改
#推送功能，可能要拆出来和搜索一起
#################################

from flask import request,Blueprint,jsonify

from .models import Questions,Answers,Users,Vote,Favorite
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

#搜索功能，返回的是关键词模糊查询的问题列表
@question.route('/api/searchquestions', methods=['POST'])
def searchquestions():
    # 获取请求中的搜索关键词
    data = request.get_json()
    query = data.get('query', '')  # 搜索关键词，默认为空字符串

    # 如果没有提供查询关键词，则返回所有问题
    if query:
        # 使用 LIKE 进行模糊查询，查找所有问题的标题和内容中包含关键词的内容
        questions = Questions.query.filter(
            (Questions.title.ilike(f'%{query}%')) | 
            (Questions.body.ilike(f'%{query}%'))
        ).all()
    else:
        questions = Questions.query.all()  # 如果没有查询关键词，返回所有问题

    # 构造问题列表
    questions_list = [{
        'id': q.id,
        'title': q.title,
        'body': q.body,
        'created_at': q.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间
        'author': q.author.username,  # 提问者用户名
    } for q in questions]

    # 返回搜索结果
    return jsonify({
        "code": 200,
        "questions": questions_list
    }), 200

# 点赞/点踩功能
@question.route('/api/vote', methods=['POST'])
def vote():
    # 获取用户的投票信息
    data = request.get_json() # 前端需要提供：{"email":xxx, “content_type”:“xxx", "content_id":“xxx", "vote_type":“xxx"}
    email = data.get('email') # 用户的email，和前面代码方法保持一致，使用邮箱检索用户id
    content_type = data.get('content_type')  # 投票内容类型：'question' 或 'answer'
    content_id = data.get('content_id')  # 对应的内容ID（问题或答案的ID）
    vote_type = data.get('vote_type')  # 投票类型（点赞还是点踩）：'upvote' 或 'downvote'

    user = Users.query.filter_by(email = email).first()

    # 参数检验
    if content_type not in ['question', 'answer']:
        return jsonify({"code": 404, "message": 'Invalid content type'})
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({"code": 404, "message": 'Invalid vote type'})
    if not content_id:
        return jsonify({"code": 404, "message": 'Content ID is required'})
    if not user:
        return jsonify({"code": 404, "message": 'User not found'})

    # 查找该用户是否已对该内容进行过投票
    existing_vote = Vote.query.filter_by(
        user_id = user.id,
        content_type = content_type,
        content_id = content_id
    ).first() # 不需要vote_type

    if existing_vote: # 如果已经投过票
        # 重复投票类型相同则返回
        if existing_vote.vote_type == vote_type:
            return jsonify({"code": 400, "message": 'You already voted this way'})

        # 重复投票类型不同则更改
        else:
            existing_vote.vote_type = vote_type
            db.session.commit() # 更新数据库
            return jsonify({"code": 200, "message": 'Your vote has been updated'})
    else: # 如果没有投过票
        new_vote = Vote(
            user_id = user.id,
            content_type = content_type,
            content_id = content_id,
            vote_type = vote_type
        ) # 创建一个新投票
        db.session.add(new_vote) # 添加到数据库
        db.session.commit()
        return jsonify({"code": 200, "message": 'Your vote has been recorded'})

# 收藏功能
@question.route('/favorite', methods=['POST'])
def favorite():
    # 获取用户的收藏信息
    data = request.get_json() # 前端需要提供：{"email":xxx, “content_type”:“xxx", "content_id":“xxx", "action":“xxx"}
    email = data.get('email') # 用户的email，和前面代码方法保持一致，使用邮箱检索用户id
    content_type = data.get('content_type')  # 收藏内容类型：'question' 或 'answer'
    content_id = data.get('content_id')  # 对应的内容ID（问题或答案的ID）
    action = data.get('action')  # 操作收藏的类型（添加收藏或取消收藏）：'add' 或 'remove'

    user = Users.query.filter_by(email=email).first()

    # 参数验证
    if content_type not in ['question', 'answer']:
        return jsonify({"code": 404, "message": 'Invalid content type'})
    if action not in ['add', 'remove']:
        return jsonify({"code": 404, "message": 'Invalid action'})
    if not content_id:
        return jsonify({"code": 404, "message": 'Content ID is required'})
    if not user:
        return jsonify({"code": 404, "message": 'User not found'})

    # 查找该用户是否已收藏过该内容
    existing_favorite = Favorite.query.filter_by(
        user_id = user.id,
        content_type = content_type,
        content_id = content_id
    ).first()

    if action == 'add': # 操作是添加收藏
        if not existing_favorite: # 如果没有收藏过，则添加到数据库
            new_favorite = Favorite(
                user_id = user.id,
                content_type = content_type,
                content_id = content_id,
                is_favorited = True
            )
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({"code": 200, "message": 'Content has been added to your favorites'})

        else: # 如果已经收藏过则返回
            return jsonify({"code": 400, "message": 'You have already added this content to your favorites'})

    elif action == 'remove': # 操作是取消收藏
        if existing_favorite: # 如果收藏过，则更改数据库
            existing_favorite.is_favorited = False
            db.session.commit()
            return jsonify({"code": 200, "message": 'Content has been removed from your favorites'})
        else: # 如果本来就未收藏过则返回
            return jsonify({"code": 400, "message": 'You have not favorited this content yet'})


