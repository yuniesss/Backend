from flask import Flask
from config import settings
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.settings')

    #from . import routes
    #app.register_blueprint(routes.bp)
    #db = 在这里初始化数据库
    return app

app = create_app()
db = SQLAlchemy(app)
