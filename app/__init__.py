#################################
#这是初始化函数，完成类的构建
#################################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .db import db
from app.auth import auth
from app.userdata import userdata
from app.question import question
from app.config import DevConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevConfig)
    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(userdata)
    app.register_blueprint(question)

    
    with app.app_context(): 
        db.create_all()

 
    return app


