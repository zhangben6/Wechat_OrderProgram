# -*- coding: utf-8 -*-
from application import app

class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl( path ):
        return path

    @staticmethod
    def buildStaticUrl(path):
        ver = "%s"%( 22222222 )
        path =  "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl( path )

    @staticmethod
    # 拼接图片显示的url地址
    def buildImageUrl(path):
        url = app.config['APP']['domain'] + app.config['UPLOAD']['prefix_url'] + path
        return url