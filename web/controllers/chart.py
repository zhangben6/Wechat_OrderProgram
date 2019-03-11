# _*_ encoding=utf-8 _*_
from flask import Blueprint,jsonify
import datetime
from common.libs.Helper import getFormatDate
from common.models.stat.StatDailySite import StatDailySite

'''
返回画图数据的对象
'''

route_chart = Blueprint('chart_page',__name__)

@route_chart.route('/dashboard')
def dashboard():
    resp = {'code':200,'msg':'操作成功','data':{}}
    resp['data'] = {}

    # 取出最近30天的营收状况
    now = datetime.datetime.now()
    date_before_30day = now + datetime.timedelta(days=-30)
    date_from = getFormatDate(date=date_before_30day, format='%Y-%m-%d')
    # 当前的时间
    date_to = getFormatDate(date=now, format='%Y-%m-%d')

    # 取数据
    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()).all()

    data = {
        'categories':[],
        'series':[
            {
                'name':"会员总数",
                'data':[]
            },{
                'name': "订单总数",
                'data': []
            }
        ]
    }

    if list:
        for item in list:
            data['categories'].append(getFormatDate(date=item.date,format='%Y-%m-%d'))
            data['series'][0]['data'].append(item.total_member_count)
            data['series'][1]['data'].append(item.total_order_count)

    resp['data'] = data
    return jsonify(resp)


@route_chart.route('/finance')
def finance():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    resp['data'] = {}

    # 取出最近30天的营收状况
    now = datetime.datetime.now()
    date_before_30day = now + datetime.timedelta(days=-30)
    date_from = getFormatDate(date=date_before_30day, format='%Y-%m-%d')
    # 当前的时间
    date_to = getFormatDate(date=now, format='%Y-%m-%d')

    # 取数据
    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()).all()

    data = {
        'categories': [],
        'series': [
            {
                'name': "日营收情况",
                'data': []
            }
        ]
    }

    if list:
        for item in list:
            data['categories'].append(getFormatDate(date=item.date, format='%Y-%m-%d'))
            data['series'][0]['data'].append(float(item.total_pay_money))

    resp['data'] = data
    return jsonify(resp)