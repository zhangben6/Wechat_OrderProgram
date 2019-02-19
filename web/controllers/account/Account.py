# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect,jsonify
from common.libs.Helper import ops_render,iPagination,getCurrentDate
from common.models.User import User
from common.libs.UrlManager import UrlManager
from application import app,db
from common.libs.user.UserService import UserService




route_account = Blueprint( 'account_page',__name__ )


@route_account.route( "/index" )
def index():
    # 分页功能的实现
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = User.query


    page_params={
        'total':query.count(),
        'page_size':app.config['PAGE_SIZE'],
        'page': page,
        'display':app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace('&={}'.format(page),''),

    }
    app.logger.info(page_params)

    pages = iPagination(page_params)

    offset = (page-1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE']*page

    list = User.query.order_by(User.uid.desc()).all()[offset:limit]

    resp_data['list'] = list
    resp_data['pages'] = pages
    return ops_render( "account/index.html",resp_data )

@route_account.route( "/info" )
def info():
    resp_data = {}
    req = request.args
    uid = int(req.get('id',0))
    reback_url = UrlManager.buildUrl('/account/index')
    if uid < 1:
        return redirect(reback_url)

    info = User.query.filter_by(uid=uid).first()
    if not info:
        return redirect(reback_url)

    resp_data['info'] = info
    print(resp_data)
    return ops_render( "account/info.html",resp_data)

@route_account.route( "/set",methods=['GET','POST'])
def set():
    default_pwd = '******'
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        uid = int(req.get('id',0))
        info = None
        if uid and uid != 0:
            info = User.query.filter_by(uid=uid).first()
        resp_data['info'] = info
        return ops_render( "account/set.html",resp_data)


    resp = {'code':200,'msg':'操作成功!','data':{}}
    req = request.values
    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    email = req['email'] if 'email' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    # 参数有效性的校验
    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的姓名!'
        return jsonify(resp)

    if mobile is None or len(mobile) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的手机号码!'
        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的邮箱!'
        return jsonify(resp)

    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的登录名!'
        return jsonify(resp)

    if login_pwd is None or len(login_pwd) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的登录密码!'
        return jsonify(resp)

    has_in = User.query.filter(User.login_name==login_name,User.uid != id).first()
    if has_in:
        resp['code'] = -1
        resp['msg'] = '该登录名已经存在,请重新输入'
        return jsonify(resp)

    # 编辑用户页面和添加用户页面的混合操作
    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        model_user = user_info
    else:

        # 添加一个新的用户到数据库
        model_user = User()
        # 生成创建时间
        model_user.created_time = getCurrentDate()
        # 生成新用户的加密密钥
        model_user.login_salt = UserService.geneSalt()

    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.email = email
    model_user.login_name = login_name
    if login_pwd != default_pwd:
        # 根据salt生成login_pwd
        model_user.login_pwd = UserService.genePwd(login_pwd,model_user.login_salt)
    model_user.updated_time = getCurrentDate()


    db.session.add(model_user)
    db.session.commit()
    return jsonify(resp) # 成功添加
















