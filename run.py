
#入口函数，在这里启动整个代码
#分功能调试的方法正在学习中

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()