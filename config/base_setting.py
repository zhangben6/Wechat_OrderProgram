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

# 帐号管理设置页面config参数设置
# 每页的数量
PAGE_SIZE = 50
# 展示栏页数
PAGE_DISPLAY = 10


STATUS_MAPPING = {
    '1':'正常',
    '0': '已删除'
}

MINA_APP = {
    'appid':'wx4d2ba3758c4fa9db',
    'appkey':'e6520fedd29877ea889d128af628038f',
    'paykey':'ADFDSAF2DF',
    'mch_id':'19216822',
    'callback_url':'/api/order/callback'
}

# 用户上传图片用到的一些设置
UPLOAD = {
    'ext':['jpg','gif','bmp','png','jpeg'],
    'prefix_path':'/web/static/upload/',
    'prefix_url':'/static/upload/'
}

# 设置自己主机的域名
APP = {
    'domain': 'http://192.168.43.136:8666',
}



# API过滤url
API_IGNORE_URLS = [
    '^/api'
]


# 订单状态的类型
PAY_STATUS_DISPLAY_MAPPING = {
    '0':'订单关闭',
    '1':'支付成功',
    '-8':'待支付',
    '-7':'待发货',
    '-6':'待确认',
    '-5':'待评价'
}











