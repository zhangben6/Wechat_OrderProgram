# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, make_response, redirect, g
from common.models.User import User
from common.libs.user.UserService import UserService
from common.libs.Helper import ops_render
import json
from application import app
from common.libs.UrlManager import UrlManager
from application import db


route_user = Blueprint( 'user_page',__name__ )

@route_user.route( "/login",methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return ops_render( "user/login.html" )

    # 设置json格式的数据用于返回错误信息给用户
    resp = {'code':200,'msg':'登录成功','data':{}}
    req = request.form
    # 取出post方式提交的数据
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    # 后台判断用户名和密码的格式是否一直
    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名'
        return jsonify(resp)

    if login_pwd is None or len(login_pwd) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的登录密码'
        return jsonify(resp)

    # 查询数据库于用户输入的用户名是否一直
    user_info = User.query.filter_by(login_name=login_name).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名和密码 -1 ~~'
        return jsonify(resp)

    if user_info.login_pwd != UserService.genePwd(login_pwd,user_info.login_salt):
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名和密码 -2 ~~'
        return jsonify(resp)

    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'],'%s#%s'%(UserService.geneAuthCode(user_info),user_info.uid))

    return response

@route_user.route( "/edit",methods=['GET','POST'])
def edit():
    if request.method == 'GET':
        return ops_render( "user/edit.html" )

    # post提交方式:  设置json返回的数据
    resp = {'code':200,'msg':'操作成功','data':{}}

    #获取前端提交过来的post数据,进行三木判断
    req = request.values
    mobile = req['mobile'] if 'mobile' in req else ''
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''

    if mobile is None or len(mobile) > 11:
        resp['code'] = -1
        resp['msg'] = '手机位数超过11位,请输入符合规范的手机号!'
        return jsonify(resp)

    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的姓名!'
        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的邮箱!'
        return jsonify(resp)

    # 提交的数据符合规范后,提交到数据库
    user_info = g.current_user
    user_info.mobile = mobile
    user_info.nickname = nickname
    user_info.email = email
    db.session.add(user_info)
    db.session.commit()
    return jsonify(resp)

@route_user.route( "/reset-pwd" )
def resetPwd():
    return ops_render( "user/reset_pwd.html" )

# 退出操作就是清理cookie,让拦截器拦截并跳到登录页面
@route_user.route('/logout')
def logout():
    response = make_response(redirect(UrlManager.buildUrl('/user/login')))
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response









