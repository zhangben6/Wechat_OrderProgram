from common.models.queue.QueueList import QueueList
from common.libs.Helper import getCurrentDate
from application import app,db
from common.models.pay.PayOrder import PayOrder
from common.models.food.Food import Food
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog

from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.pay.PayOrderItem import PayOrderItem
from common.libs.pay.WeChatService import WeChatService
import json,requests,datetime
from sqlalchemy import func

'''
python manager.py runjob -m queue/Index
'''

class JobTask():
    def __init__(self):
        pass

    def run(self,params):
        # 在测试环境下,为了方便处理,每次只limit一条数据
        list = QueueList.query.filter_by(status = -1).order_by(QueueList.id.desc()).limit(1).all()
        for item in list:
            if item.queue_name == 'pay':
                self.handlePay(item)

            # item.status = 1
            # item.update_time = getCurrentDate()
            # db.session.add(item)
            # db.session.commit()

    # 发送模板消息的处理,用于返回模板消息给用户
    def handlePay(self,item):
        data = json.loads(item.data)
        if 'member_id' not in data or 'pay_order_id' not in data:
            return False

        # 查询用户的openid用于post发送数据
        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=data['member_id']).first()
        if not oauth_bind_info:
            return False

        # 订单信息
        pay_order_info = PayOrder.query.filter_by( id=data['pay_order_id'] ).first()
        app.logger.info(pay_order_info.prepay_id)
        # 商品信息
        pay_order_items = PayOrderItem.query.filter_by( pay_order_id=pay_order_info.id).all()

        # 存放购买的商品内容具体信息
        notice_content = []

        # 更新销售数量

        if pay_order_items:
            # 月的数量
            # date_from = datetime.datetime.now().strftime("%Y-%m-01 00:00:00") # 起始时间
            # date_to = datetime.datetime.now().strftime("%Y-%m-31 23:59:59") # 月末

            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by( id=item.food_id ).first()
                if not tmp_food_info:
                    continue
                # 拼接模板消息的备注
                notice_content.append('%s %s份'%(tmp_food_info.name,item.quantity))

                # 当月的销售
                # tmp_stat_info = db.session.query(FoodSaleChangeLog,func.sum(FoodSaleChangeLog.quantity).label("total"))\
                #     .filter(FoodSaleChangeLog.food_id==item.food_id)\
                #     .filter(FoodSaleChangeLog.created_time>=date_from,FoodSaleChangeLog.created_time <= date_to).first()
                # tmp_month_count = tmp_stat_info[1] if tmp_stat_info[1] else 0


                # tmp_food_info.total_count += 1
                # tmp_food_info.month_count = 0
                # db.session.add(tmp_food_info)
                # db.session.commit()

        # 拼接模板消息
        keyword1_val = pay_order_info.note if pay_order_info.note else '无'
        keyword2_val = ','.join(notice_content)
        keyword3_val = str(pay_order_info.total_price)
        keyword4_val = str(pay_order_info.pay_time)
        keyword5_val = "" # 快递信息

        # 首先拿出对应token_access 用于发送post请求
        target_wechat = WeChatService()
        access_token = target_wechat.getAccessToken()
        url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=%s'%(access_token)
        headers = {'Content-Type':'application/json'}
        params = {
                "touser": oauth_bind_info.openid,
                "template_id": "0TYMLGfoxWFHK7UMc3p0pOVVrbtwEDGjnm5ewQ8uZKc",
                 # 页面跳转到订单页
                "page": "pages/my/order_list",
                "form_id": str(pay_order_info.prepay_id),
                "data": {
                    "keyword1": {
                        "value": keyword1_val
                    },
                    "keyword2": {
                        "value": keyword2_val
                    },
                    "keyword3": {
                        "value": keyword3_val
                    },
                    "keyword4": {
                        "value": keyword4_val
                    },
                    "keyword5": {
                        "value": keyword5_val
                    },

                },
            }

        r = requests.post(url=url,data=json.dumps(params),headers=headers)
        r.encoding = 'utf-8'

        app.logger.info(r.text)
        return True




























