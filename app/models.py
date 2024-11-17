from flask_sqlalchemy import SQLAlchemy
from app import db
#在这里进行数据库的初始化

class abc(db.Model):
    id = db.column()


#请
    