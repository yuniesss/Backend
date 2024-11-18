class Config(object):
    DEBUG = False
    TESTING = False
class DevConfig(Config):
    DEBUG = True
    #这里是使用的数据库信息
    DIALECT = 'mysql'
    DRIVER = 'pymysql'
    USERNAME = 'root'
    PASSWORD = '****'
    HOST = '127.0.0.1'
    PORT = '3306'
    DATABASE = '数据库名'
    #DATABASE_URI = '??? ??? ???'

class ProConfig(Config) :
    DEBUG = False

settings = DevConfig()