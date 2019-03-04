from web.controllers.api import route_api
from flask import request,jsonify,g
from application import app,db
import requests,json
from common.libs.Helper import getCurrentDate
from common.models.food.FoodCat import FoodCat
from common.models.food.Food import Food
from common.libs.UrlManager import UrlManager
from common.models.member.MemberCart import MemberCart
from sqlalchemy import or_


# 返回轮波图及菜品分类信息 json数据的格式
@route_api.route('/food/index')
def foodIndex():
    resp = {'code':200,'msg':'操作成功!','data':{}}
    # 查询数据库food_cat表中的所有数据,按照权重进行倒序排列
    cat_list = FoodCat.query.filter_by(status=1).order_by(FoodCat.weight.desc()).all()
    # 定义一个列表,用于返回给前端
    data_cat_list = []
    data_cat_list.append({
        'id':0,
        'name':'全部'
    })
    if cat_list:
        for item in cat_list:
            tem_data = {
                'id':item.id,
                'name':item.name
            }
            data_cat_list.append(tem_data)
    resp['data']['cat_list'] = data_cat_list

    # 取出美食列表: 按销量前三进行倒序排列
    food_list = Food.query.filter_by(status=1).order_by(Food.total_count.desc(),Food.id.desc()).limit(3).all()
    app.logger.info(food_list)
    # 按照前端index.js中的菜品数据格式进行组成拆分成同样的数据格式
    data_food_list = []
    if food_list:
        for item in food_list:
            tem_data = {
                'id': item.id,
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            data_food_list.append(tem_data)

    resp['data']['banner_list'] = data_food_list
    return jsonify(resp)

# 返回菜品的详细信息
@route_api.route('/food/search')
def foodSearch():
    # 设置返回值
    resp = {'code':200,'msg':'操作成功!','data':{}}
    req = request.values
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else 0
    p = int(req['p']) if 'p' in req else 1
    if p < 1:
        p = 1

    query = Food.query.filter_by(status=1)
    page_size = 10
    offset = (p - 1) * page_size
    if cat_id > 0:
        query = query.filter(Food.cat_id == cat_id)

    if mix_kw:
        rule = or_(Food.name.ilike("%{0}%".format(mix_kw)),Food.tags.ilike("{0}".format(mix_kw)))
        query = query.filter(rule)

    # 获取菜品对象
    food_list = query.order_by(Food.total_count.desc(),Food.id.desc()).offset(offset).limit(page_size).all()

    # 将food列表转换成json数据格式用于返回给前端
    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id':item.id,
                'name':item.name,
                'price':str(item.price),
                'min_price':str(item.price), #打折用
                'pic_url':UrlManager.buildImageUrl(item.main_image)
            }
            data_food_list.append(tmp_data)
    resp['data']['list'] = data_food_list
    resp['data']['has_more'] = 0 if len(data_food_list) < page_size else 1

    return jsonify(resp)

@route_api.route('/food/info')
def foodInfo():
    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    food_info = Food.query.filter_by(id=id).first()
    if not food_info or not food_info.status:
        resp['code'] = -1
        resp['msg'] = '美食已下架'
        return jsonify(resp)

    member_info = g.member_info
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by(member_id = member_info.id).count()


    resp['data']['info'] = {
        'id':food_info.id,
        'name':food_info.name,
        'summary':food_info.summary,
        'total_count':food_info.total_count,
        'comment_count':food_info.comment_count,
        'main_image':UrlManager.buildImageUrl(food_info.main_image),
        'price':str(food_info.price),
        'stock':food_info.stock,
        'pics':[ UrlManager.buildImageUrl(food_info.main_image) ]
    }
    resp['data']['cart_number'] = cart_number
    return jsonify(resp)














