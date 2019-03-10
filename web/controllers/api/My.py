'''
订单页面的接口处理函数
'''
from web.controllers.api import route_api
from flask import request,jsonify,g
from common.models.food.Food import Food
from common.models.member.MemberCart import MemberCart
from common.libs.member.CartService import CartService
from common.libs.Helper import selectFilterObj,getDictFilterField
from common.models.member.MemberComments import MemberComments
from common.libs.UrlManager import UrlManager
from application import app
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
import json



@route_api.route('/my/order')
def myOrderList():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    member_info = g.member_info
    req = request.values

    status = int(req['status']) if 'status' in req else 0
    # 从pay_order表中引入数据便于传输给前台
    query = PayOrder.query.filter_by(member_id=member_info.id)

    if status == -8:  # 等待付款状态
        query = query.filter(PayOrder.status == -8)
    elif status == -7:  # 待发货
        query = query.filter(PayOrder.status == 1,PayOrder.express_status==-7,PayOrder.comment_status==0)
    elif status == -6:  # 待确认收获
        query = query.filter(PayOrder.status==1,PayOrder.express_status==-6,PayOrder.comment_status==0)
    elif status == -5: # 待评价
        query = query.filter(PayOrder.status==1,PayOrder.express_status==1,PayOrder.comment_status==0)
    elif status == 1:  # 已完成
        query = query.filter(PayOrder.status==1,PayOrder.express_status==1,PayOrder.comment_status==1)
    else:
        query = query.filter(PayOrder.status == 0)

    # 获取前台传来的stauts数据,进而在数据库中查看对应的订单状态
    pay_order_list = query.order_by(PayOrder.id.desc()).all()
    app.logger.info(pay_order_list)
    # 格式化数据,构建列表,用于返回给前台展示
    data_pay_order_list = []

    if pay_order_list:

        # 根据订单表得出对象们,然后在PayOrderItem中求出对应的菜品对象们(他们有关联关系)
        pay_order_ids = selectFilterObj(pay_order_list,'id')
        pay_order_item_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids)).all()

        food_ids = selectFilterObj(pay_order_item_list,'food_id')
        food_map = getDictFilterField(Food,Food.id,'id',food_ids)

        #　前台good_list的框架
        pay_order_item_map = {}

        # 循环从表的信息
        # 循环所有下单的菜品 ,进行数据组装
        if pay_order_item_list:
            for item in pay_order_item_list:
                if item.pay_order_id not in pay_order_item_map:
                    pay_order_item_map[item.pay_order_id]=[]

                # 取出商品对象
                tmp_food_info = food_map[item.food_id]

                # 封装数据
                pay_order_item_map[item.pay_order_id].append({
                    'id':item.id,
                    'food_id':item.food_id,
                    'quantity':item.quantity,
                    'pic_url':UrlManager.buildImageUrl(tmp_food_info.main_image),
                    'name':tmp_food_info.name
                })


        # 循环主表的信息
        for item in pay_order_list:
            tmp_data = {
                'status':item.pay_status,
                'status_desc':item.status_desc,
                'date':item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                'order_number':item.order_number,
                'order_sn': item.order_sn,
                'note':item.note,
                'total_price':str(item.total_price),
                'goods_list':pay_order_item_map[item.id]
            }
            data_pay_order_list.append(tmp_data)

    # 返回数据
    resp['data']['pay_order_list'] = data_pay_order_list
    return jsonify(resp)


@route_api.route("/my/comment/list" )
def myCommentList():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    comment_list = MemberComments.query.filter_by( member_id=member_info.id )\
		.order_by(MemberComments.id.desc()).all()
    data_comment_list = []
    if comment_list:
        pay_order_ids = selectFilterObj( comment_list,"pay_order_id" )
        pay_order_map = getDictFilterField( PayOrder,PayOrder.id,"id",pay_order_ids )
        for item in comment_list:
            tmp_pay_order_info = pay_order_map[ item.pay_order_id ]
            tmp_data = {
				"date":item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
				"content":item.content,
				"order_number":tmp_pay_order_info.order_number
			}
            data_comment_list.append( tmp_data )
    resp['data']['list'] = data_comment_list
    return jsonify(resp)

























