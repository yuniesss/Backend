from flask import Flask
from config import settings
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.settings')

    #from . import routes
    #app.register_blueprint(routes.bp)
    #db = 在这里初始化数据库
    db.init_app(app)
    return app

app = create_app()

