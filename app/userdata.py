#################################
#处理用户个人信息的功能
#已完成
#################################

from flask import Blueprint,request,jsonify

from app.models import Users
from . import db


userdata = Blueprint('userdata',__name__)

@userdata.route('/api/getusername',methods = ['POST'] )
def getusername():
    data = request.get_json()
    email = data['userid']
    user_password = data['userpassword']
    existing_user = Users.query.filter_by(email=email).first()
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
    

@userdata.route('/api/changeusername',methods = ['POST'] )
def changeusername():
    data = request.get_json()
    username=data['username']
    email = data['userid']
    user_password = data['userpassword']
    with userdata.app_context():
        existing_user = Users.query.filter_by(email=email).first()
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
        

#获取用户发布的问题列表
@userdata.route('/api/getuserquestionlist',methods = ['POST'] )
def getuserquestionlist():
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


#获取用户回答列表
@userdata.route('/api/getuseranswerlist',methods = ['POST'] )
def getuseranswerlist():
    return

#获取用户关注列表
#to be done