from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app_init import db

# 用户表
class User(db.Model): # 所有模型类需要继承自 db.Model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # 用户ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱
    password_hash = db.Column(db.String(128), nullable=False)  # 密码哈希
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间

    # 与 Team 表的多对多关系
    teams = db.relationship('Team', secondary='team_membership', backref='members')
    
    # 与 Question 表的关系：一个用户可以提多个问题
    questions = db.relationship('Question', backref='author', lazy=True)

    # 与 QuestionLike 表的关系：一个用户可以对多个问题点赞
    questionlikes = db.relationship('QuestionLike', backref='liker', lazy=True)

    # 与 Answer 表的关系：一个用户可以回答多个问题
    answers = db.relationship('Answer', backref='author', lazy=True)

    # 与 AnswerLike 表的关系：一个用户可以对多个回答点赞
    answerlikes = db.relationship('AnswerLike', backref='liker', lazy=True)
    def set_password(self, password):
        """ 设置密码的哈希值 """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ 检查密码是否匹配 """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


# 团队表
class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)  # 团队ID
    name = db.Column(db.String(100), nullable=False)  # 团队名称
    description = db.Column(db.String(255), nullable=True)  # 团队描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间

    # 多对多关系：通过 TeamMembership 表建立与 User 表的关系
    members = db.relationship('User', secondary='team_membership', backref=db.backref('teams', lazy='dynamic'))

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, description={self.description})>"


# 团队成员关系表（多对多）
class TeamMembership(db.Model):
    __tablename__ = 'team_membership'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)  # 用户ID
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)  # 团队ID
    join_date = db.Column(db.DateTime, default=datetime.utcnow)  # 加入团队的时间

    user = db.relationship('User', backref=db.backref('membership', lazy=True))
    team = db.relationship('Team', backref=db.backref('membership', lazy=True))

    def __repr__(self):
        return f"<TeamMembership(user_id={self.user_id}, team_id={self.team_id})>"


# 问题表
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)  # 问题ID
    title = db.Column(db.String(255), nullable=False)  # 问题标题
    body = db.Column(db.Text, nullable=False)  # 问题内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 提问时间
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 提问者的ID

    # 通过关系与用户表关联
    author = db.relationship('User', backref=db.backref('questions', lazy=True))

    # 与回答表的关系：一个问题可以有多个回答
    answers = db.relationship('Answer', backref='question', lazy=True)

    # 与 QuestionLike 表的关系：一个问题可以有多个点赞
    likes = db.relationship('QuestionLike', backref='question', lazy=True)

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

    # 通过关系与问题表关联
    question = db.relationship('Question', backref=db.backref('answers', lazy=True))

    # 通过关系与用户表关联
    author = db.relationship('User', backref=db.backref('answers', lazy=True))

    # 与 AnswerLike 表的关系：一个问题可以有多个点赞
    likes = db.relationship('AnswerLike', backref='answer', lazy=True)

    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, created_at={self.created_at})>"

# 点赞表（问题）
class QuestionLike(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 点赞ID
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False) # 问题ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 点赞者的ID

    # 通过关系与用户表关联
    liker = db.relationship('User', backref=db.backref('questionlikes', lazy=True))

    # 通过关系与问题表关联
    question = db.relationship('Question', backref=db.backref('likes', lazy=True))

    def __repr__(self):
        return f"<QuestionLike(id={self.id}, question_id={self.question_id}, user_id={self.user_id})>"

# 点赞表（回答）
class AnswerLike(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 点赞ID
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False) # 回答ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 点赞者的ID

    # 通过关系与用户表关联
    liker = db.relationship('User', backref=db.backref('answerlikes', lazy=True))

    # 通过关系与回答表关联
    answer = db.relationship('Answer', backref=db.backref('likes', lazy=True))

    def __repr__(self):
        return f"<AnswerLike(id={self.id}, answer_id={self.answer_id}, user_id={self.user_id})>"