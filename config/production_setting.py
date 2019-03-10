'''生产环境的配置文件'''
DEBUG = True
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1/food_db?charset=utf8mb4'
SQLALCHEMY_ENCODING = 'utf8mb4'
APP = {
    'domain':'http://120.78.170.188'
}

RELEASE_VERSION = '20180308'
