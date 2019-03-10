from web.controllers.api import route_api
from flask import request,jsonify,g
from common.models.food.Food import Food
from common.models.member.MemberCart import MemberCart
from common.models.pay.PayOrder import PayOrder
from common.models.member.OauthMemberBind import OauthMemberBind
from common.libs.member.CartService import CartService
from common.libs.Helper import selectFilterObj,getDictFilterField,getCurrentDate
from common.models.member.MemberAddress import MemberAddress
from common.libs.pay.PayService import PayService
from common.libs.UrlManager import UrlManager
from application import app,db
from common.libs.pay.WeChatService import WeChatService
import json,decimal


# 获取订单的信息
@route_api.route('/order/info',methods=['POST'])
def orderInfo():
    member_info = g.member_info
    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values

    # 此时params_goods数据还是JSON格式,需要json.loads方法加息
    params_goods = req['goods'] if 'goods' in req else None

    # 添加json解析出来的数据,定义一个新的列表用来存储
    params_goods_list = []

    # 解析json数据放到列表中
    if params_goods:
        params_goods_list = json.loads(params_goods)

    # 创建一个字典 键为id值  值为购买数量
    food_dic = {}
    for item in params_goods_list:
        food_dic[item['id']] = item['number']

    #　求出商品对应的ids
    food_ids = food_dic.keys()

    # 求出商品对象
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()

    # 用于返回的列表对象
    data_food_list = []

    # 定义运费
    yun_price = pay_price = decimal.Decimal(0.00)

    if food_list:
        for item in food_list:
            tmp_data = {
                'id':item.id,
                'name': item.name,
                'price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image),
                'number':food_dic[item.id]
            }
            pay_price = pay_price + item.price * int(food_dic[item.id])
            data_food_list.append(tmp_data)

    # 定义默认的收获地址,根据前台的数据
    default_address = None
    # 丛数据库中查询书
    Address = MemberAddress.query.filter_by(is_default=1).first()
    if Address:
        default_address = {
            'name': Address.nickname,
            'mobile': Address.mobile,
            'detail': Address.province_str+Address.city_str+Address.address
        }

    resp['data']['food_list'] = data_food_list
    resp['data']['pay_price'] = str(pay_price )
    resp['data']['yun_price'] = str(yun_price)
    resp['data']['total_price'] = str(pay_price + yun_price)
    resp['data']['default_address'] = default_address


    return jsonify(resp)

# 创建订单操作
@route_api.route('/order/create',methods=['POST'])
def orderCreate():
    member_info  = g.member_info
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values

    type = req['type'] if 'type' in req else ''
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)
        
    if len(items)<1:
        resp['code'] = -1
        resp['msg'] = '下单失败:没有选择商品'
        return jsonify(resp)

    # 创建一个对象
    target = PayService()
    # params里面可以填充前台获得的数据,用于存粗到数据可
    params = {}
    resp = target.createOrder(member_info.id,items,params)

    # 最后删除对应购物车的数据
    if resp['code'] == 200 and type == 'cart':
        # 删除购物车中的对象
        CartService.deleteItem(member_info.id,items)
    return jsonify(resp)

# 订单支付
@route_api.route('/order/pay',methods=['POST'])
def orderPay():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''

    # 判断订单信息是否存在
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙,稍后再试-1'
        return jsonify(resp)

    # 为了取出openid的值
    oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_info.id).first()
    if not oauth_bind_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙,稍后再试-2'  # 为了防止钓鱼网站,不给出具体提示信息
        return jsonify(resp)


    # 设置回调地址  重要**************
    config_mina = app.config['MINA_APP']
    notify_url = 'http://120.78.170.188:8666' + config_mina['callback_url']
    app.logger.info(notify_url)
    # 创建对象,引入微信下单的方法
    target_wechat = WeChatService(merchant_key=config_mina['paykey'])

    # 获取sign 签名的方法,需要传递这些数据
    data = {
        'appid':config_mina['appid'],
        'mch_id':config_mina['mch_id'],
        'nonce_str':target_wechat.get_nonce_str(),
        'body':'订餐',
        'out_trade_no': pay_order_info.order_sn,
        'total_fee':int( pay_order_info.total_price * 100 ),
        'notify_url':notify_url,
        'trade_type':'JSAPI',
        'openid':oauth_bind_info.openid
    }

    # 重要操作: 1.生成签名  2.拼接数据转成xml格式 通过post方式发送为微信服务器,得到响应数据
    pay_info = target_wechat.get_pay_info(data)
    # 保存prepay_id为了后面发模板消息,prepay_id为第三方预付id
    pay_order_info.prepay_id = pay_info['prepay_id']
    db.session.add(pay_order_info)
    db.session.commit()
    resp['data']['pay_info'] = pay_info

    return jsonify(resp)

# 支付回调数据处理
@route_api.route('/order/callback',methods=['POST'])
def callBack():

    # 返回给微信使用
    result_data = {
        'return_code':'SUCCESS',
        'return_msg':'OK'
    }
    header = {'content-Type':'application/xml'}

    # 对微信下单成功后的返回给我们的信息(xml)进行验证
    config_mina = app.config['MINA_APP']
    target_wechat = WeChatService(merchant_key=config_mina['paykey'])

    # 取出微信给我们的xml信息,并转换成dict数据格式
    callback_data = target_wechat.xml_to_dict(request.data)
    app.logger.info(callback_data)

    # 取出sign值(签名),再生成一次sign值,做比较,防止伪造 ******************************
    sign = callback_data['sign']
    callback_data.pop('sign')
    gene_sign = target_wechat.create_sign(callback_data)
    app.logger.info(gene_sign)

    # 两次sign值做比较,如果测试官网的回调函数代码,这个步骤就要省略
    # if sign != gene_sign:
    #     result_data['return_code'] = result_data['return_msg'] = 'FAIL'
    #     return target_wechat.dict_to_xml(result_data),header

    # 对比金钱的数量是否正确 ****************************

    # 取出订单号查询对应的订单信息
    order_sn = callback_data['out_trade_no']
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    app.logger.info('牛逼',pay_order_info)
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 微信会有间隔的返回数据,如果订单的状态已经置为1,则直接返回
    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header

    # 下单成功(微信支付回调成功的操作:pay_order的状态置为1,其他状态值也要修改)
    target_pay = PayService()
    target_pay.orderSuccess(pay_order_id=pay_order_info.id,params={'pay_sn':callback_data['transaction_id']})

    # 将微信回调的信息存表
    target_pay.addPayCallbackData(pay_order_id=pay_order_info.id,data=request.data)

    return target_wechat.dict_to_xml(result_data),header


# 订单页的取消和确认收获.. 一系列操作
@route_api.route('/order/ops',methods=['POST'])
def orderOps():
    # 返回结果集为json
    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn,member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙,稍后再试'
        return jsonify(resp)

    if act == 'cancel':
        target_pay = PayService()
        ret = target_pay.closeOrder(pay_order_id=pay_order_info.id)
        if not ret:
            resp['code'] = -1
            resp['msg'] = '系统繁忙,稍后再试'
            return jsonify(resp)


    elif act == 'confirm':
        pay_order_info.express_status = 1
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()

    return jsonify(resp)




















