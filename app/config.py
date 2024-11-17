class Config(object):
    DEBUG = False
    TESTING = False
class DevConfig(Config):
    DEBUG = True
    #这里是使用的数据库信息
    #DATABASE_URI = '??? ??? ???'

class ProConfig(Config) :
    DEBUG = False