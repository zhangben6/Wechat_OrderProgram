'''
下单功能封装的类  下单并发控制,下单库存量减少
'''
from application import db,app
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrderCallbackData import PayOrderCallbackDatum
from common.libs.Helper import getCurrentDate
from common.libs.food.FoodService import FoodService
import time,hashlib,random

import decimal


class PayService():
    def __init__(self):
        pass

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
                app.logger.info('爱的就是ni',ret)
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