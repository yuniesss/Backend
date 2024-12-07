from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # 创建一个 Flask 应用实例, 传递 __name__ 给 Flask 构造函数允许 Flask 应用找到和加载配置文件
app.config.from_object('config.settings')
db = SQLAlchemy(app)

# 使用 SQLAlchemy 提供的方法来创建数据库和表
with app.app_context():
    db.create_all()