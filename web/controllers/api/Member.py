'''
小程序会员入口
'''
from web.controllers.api import route_api
from flask import request,jsonify,g
from application import app,db
import requests,json
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from common.libs.Helper import getCurrentDate
from common.libs.member.MemberService import MemberService
from common.models.food.WxShareHistory import WxShareHistory


@route_api.route('/member/login',methods=['GET','POST'])
def login():
    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values

    # 获取req中的code进而获取openid值
    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = '需要code'
        return jsonify(resp)

    # 取出openid
    openid = MemberService.getWechatOpenid(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = '调用威信出错1'
        return jsonify(resp)

    # 获取会员的信息 后用于存数据库
    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else 0
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''

    # 打印日志调试
    app.logger.info(nickname)
    app.logger.info(sex)
    app.logger.info(avatar)

    '''
    判断用户是否已经注册,如果注册了直接返回一些信息
    '''
    bind_info = OauthMemberBind.query.filter_by(openid = openid,type=1).first()
    if not bind_info:
        # 如果oauth表查不到用户信息,需要进行信息注册存进数据库
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.salt = MemberService.geneSalt()
        model_member.updated_time = model_member.created_time = getCurrentDate()
        db.session.add(model_member)
        db.session.commit()

        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id
        model_bind.type = 1
        model_bind.openid = openid
        model_bind.extra = ''
        model_bind.updated_time = model_bind.created_time = getCurrentDate()
        db.session.add(model_bind)
        db.session.commit()
        # 注册完之后就会有bind_info
        bind_info = model_bind

    # 查询用户信息,直接返回
    member_info = Member.query.filter_by(id=bind_info.member_id).first()

    # 操作完成返回给用户token数据
    token = '%s#%s'%(MemberService.geneAuthCode(member_info),member_info.id)
    resp['data'] = {'token':token}
    return jsonify(resp)


@route_api.route('/member/check-reg',methods=['GET','POST'])
def checkReg():
    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values
    app.logger.info(req)
    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = '需要code'
        return jsonify(resp)

    #取出openid
    openid = MemberService.getWechatOpenid(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = '调用微信出错'
        return jsonify(resp)

    # 查询是否有绑定关系
    bind_info = OauthMemberBind.query.filter_by(openid = openid,type=1).first()
    if not bind_info:
        resp['code'] = -1
        resp['msg'] = '该用户之前未绑定'
        return jsonify(resp)

    # 如果已经绑定取出用户绑定对应的信息
    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '未查询到用户绑定信息'
        return jsonify(resp)


    token = '%s#%s'%(MemberService.geneAuthCode(member_info),member_info.id)
    resp['data'] = {'token':token}
    return jsonify(resp)


@route_api.route('/member/share',methods=['POST'])
def memberShare():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    url = req['url'] if 'url' in req else ''
    member_info = g.member_info
    model_share = WxShareHistory()
    if member_info:
        model_share.member_id = member_info.id
    model_share.share_url = url
    model_share.created_time = getCurrentDate()
    db.session.add(model_share)
    db.session.commit()

    return jsonify(resp)


# 个人中心页面 会员消息的获取
@route_api.route('/member/info')
def memeberInfo():
    resp = {'code':200,'msg':'操作成功!','data':{}}
    member_info = g.member_info
    resp['data']['info'] = {
        'nickname':member_info.nickname,
        'avatar_url':member_info.avatar,
        'mobile':member_info.mobile    # api接口获取不了手机号
    }
    return jsonify(resp)


















