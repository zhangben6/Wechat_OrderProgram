# -*- coding: utf-8 -*-
from flask import Blueprint,  g
from common.libs.Helper import ops_render


route_index = Blueprint( 'index_page',__name__ )

@route_index.route("/")
def index():
    current_user = g.current_user
    return ops_render( "index/index.html")