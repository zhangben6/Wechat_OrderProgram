# -*- coding: utf-8 -*-
from flask import Blueprint,  g
from common.libs.Helper import ops_render,getFormatDate
from common.models.stat.StatDailySite import StatDailySite
import datetime

route_index = Blueprint( 'index_page',__name__ )

@route_index.route("/")
def index():

    # 定义返回给前端用于展示的数据格式
    resp = {
        'data':{
            'finance':{
                'today':0,
                'month':0
            },
            'member':{
                'total_new':0,
                'month_new':0,
                'total':0
            },
            'order':{
                'today':0,
                'month':0
            },
            'shared':{
                'today': 0,
                'month': 0
            }
        }
    }
    # 取出最近30天的营收状况
    now = datetime.datetime.now()
    date_before_30day = now + datetime.timedelta(days=-30)
    date_from = getFormatDate(date = date_before_30day,format='%Y-%m-%d')
    # 当前的时间
    date_to = getFormatDate(date=now,format='%Y-%m-%d')

    list = StatDailySite.query.filter(StatDailySite.date>=date_from)\
            .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()).all()

    data = resp['data']
    if list:
        for item in list:
            data['finance']['month'] += item.total_pay_money
            data['member']['month_new'] += item.total_new_member_count
            data['member']['total'] = item.total_member_count
            data['order']['month'] += item.total_order_count
            data['shared']['month'] += item.total_shared_count

            if getFormatDate(date = item.date,format='%Y-%m-%d') == date_to:
                data['finance']['today'] = item.total_pay_money
                data['member']['today_new'] = item.total_new_member_count
                data['order']['today'] = item.total_order_count
                data['shared']['today'] = item.total_shared_count  # 数据不对
    return ops_render( "index/index.html",resp)













