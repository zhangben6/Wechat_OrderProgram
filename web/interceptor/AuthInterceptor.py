'''
统一拦截器  判断登录是否存在cookies
'''

from application import app
from flask import request, redirect, g
from common.models.User import User
from common.libs.user.UserService import UserService
from common.libs.UrlManager import UrlManager
import re


@app.before_request
def before_request():

    ignore_urls = app.config['IGNORE_URLS']
    ignore_check_login_urls = app.config['IGNORE_CHECK_LOGIN_URLS']
    # 获取页面的url地址
    path = request.path

    pattern = re.compile('%s'%'|'.join(ignore_check_login_urls))
    if pattern.match(path):
        return

    user_info = check_login()

    # flask中的g方法可以获取用户的状态,传入'/'的视图处理函数
    g.current_user = None
    if user_info:
        g.current_user = user_info

    # app.logger.info(user_info)

    pattern = re.compile('%s' % '|'.join(ignore_urls))
    if pattern.match(path):
        return

    if not user_info:
        return redirect(UrlManager.buildUrl('/user/login'))

    return


'''
判断用户是否已经登录
'''
def check_login():
    cookies = request.cookies
    auth_cookie = cookies[app.config['AUTH_COOKIE_NAME']] if app.config['AUTH_COOKIE_NAME'] in cookies else None
    # app.logger.info(auth_cookie)
    if auth_cookie is None:
        return False
    auth_info = auth_cookie.split('#')
    if len(auth_info) != 2:
        return False
    try:
        user_info = User.query.filter_by(uid=auth_info[1]).first()
    except Exception:
        return False

    if user_info is None:
        return False

    # 判断cookie是否一致
    if auth_info[0] != UserService.geneAuthCode(user_info):
        return False

    return user_info