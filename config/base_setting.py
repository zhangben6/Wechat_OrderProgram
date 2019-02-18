'''基础配置文件'''

# Flask启动配置端口
SERVER_PORT = 8666

# Flask默认情况下debug模式是关闭的(本地测试环境开启)
DEBUG = False

# 默认不打印输出
SQLALCHEMY_ECHO = False

AUTH_COOKIE_NAME = 'mooc_food'

# 过滤url
IGNORE_URLS = [
    '^/user/login'
]

IGNORE_CHECK_LOGIN_URLS = [
    '^/static',
    '^/favicon.ico'
]