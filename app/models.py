#################################
#model
#我把数据库类名都加了一个s，麻烦您查找替换
#################################


from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from .db import db
# 用户表

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # 用户ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱
    password_hash = db.Column(db.String(5), nullable=False)  # 密码哈希
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间


    def set_password(self, password):
        """ 设置密码的哈希值 """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ 检查密码是否匹配 """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Users(id={self.id}, username={self.username}, email={self.email})>"
    
    @classmethod
    def get_user_by_email(cls, email):
        user = cls.query.filter_by(email=email).first()
        return user

    @classmethod
    def login(cls, email, password):
        """ 根据邮箱和密码验证登录 """
        user = cls.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None


# 问题表
class Questions(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)  # 问题ID
    title = db.Column(db.String(255), nullable=False)  # 问题标题
    body = db.Column(db.Text, nullable=False)  # 问题内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 提问时间
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 提问者的ID

    # 通过关系与用户表关联
    author = db.relationship('Users', backref=db.backref('questions', lazy=True))

    # 与回答表的关系：一个问题可以有多个回答
    answers = db.relationship('Answers', backref='questions', lazy=True)

    def __repr__(self):
        return f"<Questions(id={self.id}, title={self.title}, created_at={self.created_at})>"


# 回答表
class Answers(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)  # 回答ID
    body = db.Column(db.Text, nullable=False)  # 回答内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 回答时间
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)  # 所属问题ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 回答者的ID

    # 通过关系与用户表关联
    author = db.relationship('Users', backref=db.backref('answers', lazy=True))

    def __repr__(self):
        return f"<Answers(id={self.id}, question_id={self.question_id}, created_at={self.created_at})>"


#评论表
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)  # 评论ID
    content_type = db.Column(db.Enum('question', 'answer', name='content_type_enum'), nullable=False)  # 评论内容类型
    content_id = db.Column(db.Integer, nullable=False)  # 评论的内容ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 评论的用户ID
    body = db.Column(db.Text, nullable=False)  # 评论内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 评论时间

    # 与用户表的关系
    author = db.relationship('Users', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return f'<Comment {self.id} on {self.content_type} {self.content_id}>'
    

#点赞表
class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)  # 投票ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 投票的用户ID
    content_type = db.Column(db.Enum('question', 'answer', name='content_type_enum'), nullable=False)  # 投票内容类型
    content_id = db.Column(db.Integer, nullable=False)  # 投票的内容ID
    vote_type = db.Column(db.Enum('upvote', 'downvote', name='vote_type_enum'), nullable=False)  # 投票类型（点赞还是点踩）

    # 与用户表的关系
    voter = db.relationship('Users', backref=db.backref('votes', lazy=True))

    def __repr__(self):
        return f'<Vote {self.vote_type} on {self.content_type} {self.content_id}>'

# 收藏表
class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)  # 收藏ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 收藏的用户ID
    content_type = db.Column(db.Enum('question', 'answer', name='content_type_enum'), nullable=False)  # 收藏内容类型
    content_id = db.Column(db.Integer, nullable=False)  # 收藏的内容ID
    is_favorited = db.Column(db.Boolean, nullable=False, default=True)  # 是否已收藏
    # 设置这个字段标记是否收藏而不是通过添加/删减收藏表条目，是为保留历史记录（即使用户取消收藏，该条记录仍然存在，只是 is_favorited 被标记为 False）
    # 避免频繁的收藏和取消收藏操作影响性能或者对数据库造成潜在影响

    # 与用户表的关系
    user = db.relationship('Users', backref=db.backref('favorites', lazy=True))

    def __repr__(self):
        return f'<Favorite {self.content_type} {self.content_id} by user {self.user_id}>'
