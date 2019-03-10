'''本地开发环境配置文件'''

# 测试环境开始调试功能
DEBUG = True

# 将所有的SQL语句打印出来
SQLALCHEMY_ECHO = False

# SQLAlchemy 连接mysql数据库
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1/food_db'

# 去掉烦人的提示
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 设置编码UTF8
SQLALCHEMY_ENCODING = 'utf-8'
