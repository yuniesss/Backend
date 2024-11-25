import os

class Config(object):
    # 通用配置
    SECRET_KEY = os.urandom(24)  # session 密钥
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用对象修改追踪
    SQLALCHEMY_ECHO = False  # 默认不输出 SQL 语句

class DevConfig(Config):
    # 开发环境配置
    DEBUG = True
    # 配置数据库连接 URI
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/team_qna_platform' 

    #notice！！！！ 根据实际需要把上面的root改成你的数据库的用户名 password改为实际的密码
    
    # 其他开发环境特有的配置
    CACHE_TYPE = "redis"  # 可以根据需要使用缓存
    LOGGING_LEVEL = 'DEBUG'  # 开发环境通常需要更详细的日志

class ProConfig(Config):
    # 生产环境配置
    DEBUG = False
    # 配置数据库连接 URI
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/team_qna_platform'
    
    # 生产环境的一些配置
    CACHE_TYPE = "redis"  # 使用 Redis 缓存
    LOGGING_LEVEL = 'ERROR'  # 生产环境通常只记录错误日志
    SQLALCHEMY_POOL_SIZE = 10  # 数据库连接池大小
    SQLALCHEMY_MAX_OVERFLOW = 5  # 超出连接池的最大连接数

# 可以通过环境变量 FLASK_ENV 来选择配置类
environment = os.getenv('FLASK_ENV', 'development')  # 默认使用开发环境
if environment == 'development':
    settings = DevConfig
elif environment == 'production':
    settings = ProConfig
else:
    settings = Config  # 默认配置

