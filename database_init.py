#初始化数据库的函数，直接运行这个函数即可
from app import create_app, db
from app.models import Users

app = create_app()

with app.app_context():
    # 删除所有用户数据（可选，取决于你是否想要清空数据）
    db.session.query(Users).delete()
    db.session.commit()

    # 创建新用户
    users = [
        Users(username='john', email='john@example.com'),
        Users(username='jane', email='jane@example.com'),
        Users(username='xsy', email='879766866@qq.com')
    ]

    # 添加用户到数据库
    for user in users:
        user.set_password('11111')  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交事务