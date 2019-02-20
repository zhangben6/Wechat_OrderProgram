# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, jsonify
from common.libs.Helper import ops_render,iPagination,getCurrentDate
from common.models.member.Member import Member
from common.libs.UrlManager import UrlManager
from application import app,db



route_member = Blueprint( 'member_page',__name__ )

@route_member.route( "/index" )
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['q']) else 1
    query = Member.query

    if 'status' in req and int(req['status'])>-1:
        query = query.filter(Member.status == int(req['status']))

    if 'mix_kw' in req:
        # 对数据库实体类进行like查询,类似于模糊查询
        query = query.filter(Member.nickname.ilike('%{0}%'.format(req['mix_kw'])))


    page_params = {
        'total':query.count(),
        'page_size':app.config['PAGE_SIZE'],
        'page':page,  # 当前第几页
        'display':app.config['PAGE_DISPLAY'], # 总页数
        'url':request.full_path.replace('&p={}'.format(page),'')  # 去掉原来分页的$=xx形式
    }

    # 得到一个统一分页的封装类
    pages = iPagination(page_params)

    # 得出设置分页的结果列表(****** 这是错误的方法 *********)
    # offset = ( page - 1 ) * app.config['PAGE_SIZE'],
    # list = query.order_by(Member.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE']
    list = query.order_by(Member.id.desc()).all()[offset:limit]
    # app.logger.info(list)


    resp_data['list'] = list
    # 传入自定义模板文件用到的变量
    resp_data['pages'] = pages

    # 向模板传入req中的search_con参数
    resp_data['search_con'] = req

    resp_data['current'] = 'index'
    # 传入设置文件中的定义好的判断字段
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    app.logger.info(resp_data)
    return ops_render( "member/index.html",resp_data)

@route_member.route( "/info" )
def info():
    resp_data = {}
    req = request.args
    id = int(req.get('id',0))
    reback_url = UrlManager.buildUrl("/member/index")
    if id < 1:
        return redirect(reback_url)
    info = Member.query.filter_by(id = id).first()
    if not info:
        return redirect(reback_url)

    resp_data['info'] = info
    resp_data['current'] = 'index'

    return ops_render( "member/info.html",resp_data)

@route_member.route( "/set",methods=['GET','POST'])
def set():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        id = int(req.get('id',0))
        reback_url = UrlManager.buildUrl("/member/index")
        if id < 1:
            return redirect(reback_url)
        info = Member.query.filter_by(id=id).first()
        if not info:
            return redirect(reback_url)
        resp_data['info'] = info
        resp_data['current'] = 'index'
        app.logger.info(resp_data)
        return ops_render( "member/set.html",resp_data)

    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values
    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的姓名'
        return jsonify(resp)

    # 查询用户的信息
    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code']= -1
        resp['msg'] = '指定会员不存在'
        return jsonify(resp)
    member_info.nickname = nickname
    member_info.update_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)





@route_member.route( "/comment" )
def comment():
    return ops_render( "member/comment.html" )
