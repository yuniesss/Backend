#################################
#组队功能
#处理组队，组队的创建，查询，更改
#################################

from flask import Blueprint,request,jsonify
from datetime import datetime
from datetime import timezone
from datetime import timedelta
SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)
from app.models import Users
from . import db
from .models import Questions,Answers,Users,Vote,Favorite,Team

team = Blueprint('team',__name__)
@team.route('/api/getmyteam', methods=['POST'])
def getmyteam():
    data = request.get_json()
    email = data.get('email')
    existing_user = Users.query.filter_by(email=email).first()
    team_list = [{'id': q.id, 'title': q.title, 'body': q.description, 'total_members':q.total_members,
                              'created_at': q.created_at.isoformat(sep=' '),'creater':q.author.username,
                              'expiration_date':q.expiration_date.isoformat(sep=' '), 'current_members':q.current_members,
                              'is_expired': q.is_expired(),'members':q.members,
                              } for q in existing_user.teams]
    print(team_list)

    return jsonify({
        "code":200,
        "teams":team_list,
        }
        )


@team.route('/api/teamlist', methods=['POST'])
def teamlist():
    data = request.get_json()
    page_size = data.get('page_size')
    page = data.get('page')
    start = (page-1) * page_size
    
    total_items = Team.query.count()
    teams = Team.query.order_by(Team.id.desc()).offset(start).limit(page_size).all()
    team_list = [{'id': q.id, 'title': q.title, 'body': q.description, 'total_members':q.total_members,
                              'created_at': q.created_at.isoformat(sep=' '),'creater':q.author.username,
                              'expiration_date':q.expiration_date.isoformat(sep=' '), 'current_members':q.current_members,
                              'is_expired': q.is_expired(),
    'members': [ user.email for i in q.get_members() if (user := Users.query.filter_by(id=i).first()) is not None]  # 检查用户是否存在
} for q in teams]

    return jsonify({
        "code":200,
        "list":team_list,
        "total":total_items,
        }
        )


@team.route('/api/createteam', methods=['POST'])
def create_team():
    """创建组队"""
    data = request.get_json() # 前端需要提供：{"title":xxx, “description”:“xxx", "total_members":“xxx", "expiration_date":“xxx"}
    title = data.get('title') # 标题
    description = data.get('description') # 描述
    total_members = data.get('total_members') # 总人数
    expiration_date_str = data.get('expiration_date')  # 截止日期
    
    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S')
    expiration_date=expiration_date.replace(tzinfo=SHA_TZ)
    print(expiration_date)
    email=data['email']
    existing_user = Users.query.filter_by(email=email).first()
    if not title or not description or not total_members:
        return jsonify({"code": 404, "message": 'Missing necessary parameters'})
    new_team = Team(
        title = title,
        description = description,
        total_members = total_members,
        expiration_date = expiration_date,
        created_at=datetime.now().astimezone(SHA_TZ),
        user_id=existing_user.id,
    )
    print(new_team.expiration_date)
    db.session.add(new_team)
    db.session.commit()
    return jsonify({"code": 200, "message": 'The team is created successfully','team_id': new_team.id})

@team.route('/api/jointeam', methods=['POST'])
def join_team():
    """响应组队"""
    data = request.get_json() # 前端需要提供：{"email":xxx, “team_id”:“xxx"}
    email = data.get('email')  # 用户的email，和前面代码方法保持一致，使用邮箱检索用户id
    team_id = data.get('team_id')

    # 检查用户是否存在
    user = Users.query.filter_by(email = email).first()
    if not user:
        return jsonify({"code": 404, "message": 'User does not exist'})

    # 检查组队是否存在
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"code": 404, "message": 'Team does not exist'})
    if user.id==team.user_id:
        return jsonify({"code": 404, "message": '发起者不可响应'})
    # 组队已过期
    if team.is_expired():
        return jsonify({"code": 400, "message": 'The team has expired'})

    # 组队已满
    if team.current_members >= team.total_members:
        return jsonify({"code": 400, "message": 'The team is full'})

    # 检查用户是否已经加入组队
    members = team.get_members()
    if user.id in members:
        return jsonify({"code": 400, "message": 'The user has joined the team'})

    # 加入组队
    team.add_member(user.id)
    db.session.commit()

    return jsonify({"code": 200, "message": 'Successfully joined the team', 'current_members': team.current_members})

@team.route('/api/view_team', methods=['POST'])
def view_team():
    """查看组队信息"""
    data = request.get_json() # 前端需要提供：{"team_id":xxx}
    team_id = data.get('team_id')

    team = Team.query.get(team_id)
    if not team:
        return jsonify({"code": 404, "message": 'Team does not exist'})

    # 获取成员信息
    member_ids = team.get_members()
    members = []
    for user_id in member_ids:
        user = Users.query.get(user_id)
        if user:
            members.append({'user_id': user.id, 'username': user.username, 'email':user.email})

    team_info = {
        'id': team.id,
        'title': team.title,
        'description': team.description,
        'total_members': team.total_members,
        'current_members': team.current_members,
        'expiration_date': team.expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
        'is_expired': team.is_expired(),
        'members': members
    }

    return jsonify({"code": 200, 'team': team_info})

