'''
__init__入口文件
'''

from flask import Blueprint

route_api = Blueprint('api_page',__name__)
from web.controllers.api.Member import *
from web.controllers.api.Food import *

@route_api.route('/')
def index():
    return 'Mina Api V1.0'