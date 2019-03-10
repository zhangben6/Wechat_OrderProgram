'''
下单功能封装的类  下单并发控制,下单库存量减少
'''
from application import db,app
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrderCallbackData import PayOrderCallbackData
from common.libs.Helper import getCurrentDate
from common.libs.food.FoodService import FoodService
from common.libs.queue.QueueService import QueueService
import time,hashlib,random
import decimal


class PayService():
    def __init__(self):
        pass

    # 创建订单的系列操作
    def createOrder(self,member_id,items=None,params=None):
        resp = {'code': 200, 'msg': '操作成功', 'data': {}}

        # 付款价格
        pay_price = decimal.Decimal(0.00)
        # 设置continue的次数
        continue_cnt = 0
        # 为了query查询使用
        foods_id = []
        for item in items:
            if decimal.Decimal(item['price']) < 0:
                continue_cnt += 1
                continue
            # 商品总数量的价格
            pay_price = pay_price + decimal.Decimal(item['price']) * item['number']
            foods_id.append(item['id'])

        if continue_cnt >= len(items):
            resp['code'] = -1
            resp['msg'] = '商品items为空'
            return resp

        # 前台获得的运费价格
        yun_price = params['yun_price'] if params and 'yun_price' in params else 0
        # 前台获得的备注
        note = params['note'] if params and 'note' in params else ''

        yun_price = decimal.Decimal(yun_price) # 转换格式

        # 总价钱
        total_price = yun_price + pay_price

        # 并发处理
        try:
            tmp_food_list = db.session.query(Food).filter( Food.id.in_(foods_id) )\
                .with_for_update().all()

            # 行级锁生效,此时需要向两个表内添加数据存数据库

            # 构建字典格式的数据用于返回给前台 {菜品id:对应库存}
            tmp_food_stock_mapping = {}
            for tmp_item in tmp_food_list:
                tmp_food_stock_mapping[tmp_item.id] = tmp_item.stock

            # 主表字段数据填充 par_order
            model_pay_order = PayOrder()
            model_pay_order.order_sn = self.geneOrderSn()
            model_pay_order.member_id = member_id
            model_pay_order.total_price = total_price
            model_pay_order.yun_price = yun_price
            model_pay_order.pay_price = pay_price
            model_pay_order.note = note
            model_pay_order.status = -8  # 提交订单后表示待付款状态 -8表示
            model_pay_order.express_status = -8
            model_pay_order.updated_time = model_pay_order.created_time = getCurrentDate()
            db.session.add(model_pay_order)

            for item in items:
                # 剩下的库存量
                tmp_left_stock = tmp_food_stock_mapping[item['id']]
                if decimal.Decimal(item['price']) < 0:
                    continue

                # 购买的数量超过库存量
                if int(item['number']) > int(tmp_left_stock):
                    raise Exception('您购买的美食过于火爆,剩余%s,您购买:%s'%(tmp_left_stock,item['number']))

                # 更新库存
                tmp_ret = Food.query.filter_by(id=item['id']).update({
                    'stock':int(tmp_left_stock)-int(item['number'])
                })

                if not tmp_ret:
                    raise Exception('下单失败请重新下单')

                # 通过以上考验,填充第二章数据库中的表  payorderitem
                tmp_pay_item = PayOrderItem()
                tmp_pay_item.pay_order_id = model_pay_order.id  # 订单id
                tmp_pay_item.member_id = member_id
                tmp_pay_item.quantity = item['number']
                tmp_pay_item.price = item['price']
                tmp_pay_item.food_id = item['id']
                tmp_pay_item.note = note
                tmp_pay_item.updated_time = tmp_pay_item.created_time = getCurrentDate()
                db.session.add(tmp_pay_item)

                # 下完单更新后台的库存量  FoodStockChangeLog
                ret = FoodService.setStockChangeLog(item['id'],-item['number'],'在线购买')
            # 提交事物
            db.session.commit()
            resp['data'] = {
                'id':model_pay_order.id,
                'order_price':str(total_price),
                'total_price':str(total_price)
            }
        except Exception as e:
            # 出现错误,事物回滚
            db.session.rollback()
            print(e)
            resp['code'] = -1
            resp['msg'] = '下单失败,请重新下单'
            resp['msg'] = str(e)
            return resp


        return resp

    # 取消订单的操作
    def closeOrder(self,pay_order_id=0):
        if pay_order_id < 1:
            return False
        pay_order_info = PayOrder.query.filter_by(id=pay_order_id,status=-8).first()
        if not pay_order_info:
            return False

        # 归还数据
        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
        if pay_order_items:
            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if tmp_food_info:
                    tmp_food_info.stock = tmp_food_info.stock + item.quantity
                    tmp_food_info.update_time = getCurrentDate()
                    db.session.add(tmp_food_info)
                    db.session.commit()
                    FoodService.setStockChangeLog(item.food_id,item.quantity,'订单取消')

        pay_order_info.status = 0  # 代表无效状态
        pay_order_info.express_status = 0  # 代表无效状态
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return True

    # 此方法只随机生成payorder表的order_sn 随机数 md5方式
    def geneOrderSn(self):
        m = hashlib.md5()
        sn = None
        while True:
            str = "%s-%s"%(int(round(time.time() * 1000)),random.randint(0,9999999))
            m.update(str.encode('utf-8'))
            sn = m.hexdigest()
            if not PayOrder.query.filter_by(order_sn=sn).first():
                break
        return sn

    # 重新修改生成订单号的方式
    def geneOrderSn1(self):
        now = time.time()
        localtime = time.localtime(now)
        date_format_localtime = time.strftime("%Y%m%d%H%M%S", localtime)
        return int(date_format_localtime)

    # 下单成功后的操作(下单成功的操作)
    def orderSuccess(self,pay_order_id=0,params=None):
        try:
            pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()

            # 如果是以下情况的话,说明不用处理
            if not pay_order_info or pay_order_info.status not in [-8,-7]:
                return True


            # 在pay_order表中添加第三方号流水信息
            pay_order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''
            pay_order_info.status = 1

            # 设置快递状态
            pay_order_info.express_status = -7
            pay_order_info.pay_time = getCurrentDate()
            pay_order_info.updated_time = getCurrentDate()
            db.session.add(pay_order_info)

            # 付款成功后,改变销售记录明细表的信息 ***************

            # 首先取出items中总共有多少中商品
            pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
            for order_item in pay_order_items:
                # 购买单品的件数记录值 ---> food_sale_change_log 表
                tmp_model_sale_log = FoodSaleChangeLog()
                tmp_model_sale_log.food_id = order_item.food_id
                tmp_model_sale_log.quantity = order_item.quantity
                tmp_model_sale_log.price = order_item.price
                tmp_model_sale_log.member_id = order_item.member_id
                tmp_model_sale_log.created_time = getCurrentDate()
                db.session.add(tmp_model_sale_log)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return False

        # 回调成功的话 去 queue_list加入一条消息
        QueueService.addQueue('pay',{
            'member_id':pay_order_info.member_id,
            'pay_order_id':pay_order_info.id
        })

    # 添加支付成功后的回调信息
    def addPayCallbackData(self,pay_order_id=0,type='pay',data=''):
        model_callback = PayOrderCallbackData()
        model_callback.pay_order_id = pay_order_id
        if type == 'pay':
            model_callback.pay_data = data
            model_callback.refund_data = ''

        # 如果是回调信息是退款信息
        else:
            model_callback.refund_data = data  # 退款回调信息
            model_callback.pay_data = ''
        app.logger.info(model_callback.pay_data)

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True
