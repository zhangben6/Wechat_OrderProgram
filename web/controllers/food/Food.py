# -*- coding: utf-8 -*-
from _decimal import Decimal

from flask import Blueprint, request, jsonify, redirect
from common.libs.Helper import ops_render,getCurrentDate
from common.models.food.FoodCat import FoodCat
from common.models.food.Food import Food
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.libs.UrlManager import UrlManager
from application import app,db


route_food = Blueprint( 'food_page',__name__ )

@route_food.route( "/index" )
def index():
    return ops_render( "food/index.html" )

@route_food.route( "/info" )
def info():
    return ops_render( "food/info.html" )


@route_food.route( "/set",methods=['GET','POST'])
def set():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        id = int(req.get('id',0))
        info = Food.query.filter_by(id=id).first()
        if info and info.status != 1:
            return redirect(UrlManager.buildUrl("/food/index"))

        cat_list = FoodCat.query.all()
        resp_data['info'] = info
        resp_data['cat_list']  = cat_list
        resp_data['current'] = index
        return ops_render("food/set.html", resp_data)

    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    name = req['name'] if 'name' in req else ''
    price = req['price'] if 'price' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''
    summary = req['summary'] if 'summary' in req else ''
    stock = int(req['stock']) if 'stock' in req else ''
    tags = req['tags'] if 'tags' in req else ''
    price = Decimal(price).quantize(Decimal('0.00'))

    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = '请选择分类~'
        return jsonify(resp)
    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的名称'
        return jsonify(resp)
    if price <= 0:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的售卖价格~'
        return jsonify(resp)
    if main_image is None or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = '请上传封面图'
        return jsonify(resp)
    if summary is None or len(summary) < 10:
        resp['code'] = -1
        resp['msg'] = '请输入图片描述,不能少于10个字符~'
        return jsonify(resp)
    if stock < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的库存量'
        return jsonify(resp)
    if tags is None or len(tags)<1:
        resp['code'] = -1
        resp['msg'] = '请输入标签,便于搜索~'
        return jsonify(resp)
    food_info = Food.query.filter_by(id=id).first()
    # 定义之前的库存变量为before_stock
    before_stock = 0
    if food_info:
        model_food = food_info
        before_stock = model_food.stock
    else:
        model_food = Food()
        model_food.status = 1
        model_food.created_time = getCurrentDate()

    model_food.cat_id = cat_id
    model_food.name = name
    model_food.price = price
    model_food.main_image = main_image
    model_food.summary = summary
    model_food.stock = stock
    model_food.tags = tags
    model_food.updated_time = getCurrentDate()

    db.session.add(model_food)
    db.session.commit()

    # 要关联到库存表的操作
    model_stock_change = FoodStockChangeLog()
    model_stock_change.food_id = model_food.id
    # 库存变更记录
    model_stock_change.unit = int(stock) - int(before_stock)
    # 现有库存量
    model_stock_change.total_stock = stock
    model_stock_change.note = ''
    model_stock_change.created_time = getCurrentDate()
    db.session.add(model_stock_change)
    db.session.commit()
    return jsonify(resp)





@route_food.route( "/cat" )
def cat():
    # 分页功能的实现
    resp_data = {}
    req = request.values
    query = FoodCat.query

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(FoodCat.status == req['status'])

    list = query.order_by(FoodCat.weight.desc(),FoodCat.id.desc()).all()
    resp_data['list'] = list
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['current'] = 'cat'
    # search_con代表请求中的参数对象,发送status对应的值
    resp_data['search_con'] = req
    app.logger.info(resp_data)
    return ops_render( "food/cat.html",resp_data)

@route_food.route( "/cat-set",methods=['GET','POST'])
def catSet():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        id = int(req.get('id',0))
        info = None
        if id:
            info = FoodCat.query.filter_by(id=id).first()
        resp_data['info'] = info
        resp_data['current'] = 'cat'
        return ops_render( "food/cat_set.html",resp_data)

    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    name = req['name'] if 'name' in req else ''
    weight = int( req['weight'] ) if ('weight' in req and int( req['weight'])>0 ) else 1

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的分类名称'
        return jsonify(resp)
    food_cat_info = FoodCat.query.filter_by(id=id).first()
    if food_cat_info:
         food_cat_info.name = name
         food_cat_info.weight = weight
         food_cat_info.updated_time = getCurrentDate()
         db.session.add(food_cat_info)
    else:
         model_food_cat = FoodCat()
         model_food_cat.created_time = getCurrentDate()
         model_food_cat.name = name
         model_food_cat.weight = weight
         model_food_cat.updated_time = getCurrentDate()
         db.session.add(model_food_cat)

    db.session.commit()
    return jsonify(resp)

@route_food.route('/cat-ops',methods=['POST'])
def catOps():
    # 定义json数据格式用于交互
    resp = {'code':200,'msg':'操作成功!','data':{}}
    req = request.values

    id = req['id'] if 'id' in req else ''
    act = req['act'] if 'act' in req else ''
    if not id :
        resp['code'] = -1
        resp['msg'] = '请选择要操作的帐号'
        return jsonify(resp)

    if act not in ['remove','recover']:
        resp['code'] = -1
        resp['msg'] = '操作有误,请重试'
        return jsonify(resp)

    food_cat_info = FoodCat.query.filter_by(id=id).first()
    if not food_cat_info:
        resp['code'] = -1
        resp['msg'] = '指定帐号不存在'
        return jsonify(resp)

    # 接下来是查到有用户数据的判断
    if act == 'remove':
        food_cat_info.status = 0
    elif act == 'recover':
        food_cat_info.status = 1

    app.logger.info(food_cat_info)

    # 保存进数据库
    # 更新用户的'更新'字段
    food_cat_info.update_time = getCurrentDate()

    db.session.add(food_cat_info)
    db.session.commit()
    return jsonify(resp)





