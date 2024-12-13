看我看我看我！

分模块了

运行请直接运行run.py
app内每一个py都有开头注释，请阅读

应该是调通了

然后代码里有一个压缩包是接口文档，前后端的接口基本按照那个格式进行
删去了‘info’栏
把‘data’栏里内容直接展开
具体的格式参考具体代码内容

关于Blueprint（蓝图）
在 Flask 中，蓝图（Blueprint）是一种组织代码的方式，它允许你将不同的功能模块化，使得大型应用的开发和维护更加容易。蓝图可以被看作是一个“迷你”应用，它包含了自己的视图函数、模板和静态文件。你可以在蓝图中定义路由和视图，然后将蓝图注册到主 Flask 应用中。

以下是蓝图的基本用法：以auth.py为例

创建蓝图对象：
1.首先，你需要从 flask 模块导入 Blueprint 类，并创建一个蓝图对象。
	from flask import Blueprint
	bp = Blueprint('bp', __name__)
	在这里，'auth 是蓝图的名称，__name__ 是当前模块的名称(不用动）。

2.定义路由和视图函数：//这个写在python.py
	在蓝图对象上使用 route() 装饰器来定义路由和对应的视图函数。
	@auth.route('/')
	def index():
    		return "Hello, Blueprint!"

3.注册蓝图到 Flask 应用：//这里的代码写在__init__的creat_app函数里
	在你的主应用中，你需要注册蓝图对象。
	from flask import Flask

	app = Flask(__name__)
	app.register_blueprint(auth, url_prefix='/myblueprint')
	url_prefix 是一个可选参数，它允许你为蓝图中的所有路由添加一个前缀。


