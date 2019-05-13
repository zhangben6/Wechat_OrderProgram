'''封装Flask的全局变量,包括app,数据库等'''

from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import os

class Application(Flask):
    def __init__(self,import_name,template_folder=None,root_path=None):
        super(Application,self).__init__(import_name,template_folder=template_folder,root_path=root_path,static_folder=None)

        # 加载默认配置文件
        self.config.from_pyfile('config/base_setting.py')

        # 通过在终端设置不同的环境变量，加载本地和生产环境配置文件
        if 'ops_config' in os.environ:
            self.config.from_pyfile('config/%s_setting.py'%os.environ['ops_config'])

        # 配置db变量,相当于db= SQLAlchemy(app)
        db.init_app(self)


db = SQLAlchemy()
app = Application(__name__,template_folder=os.getcwd()+'/web/templates',root_path=os.getcwd())
manager = Manager(app)


'''
在模板上使用函数
'''
from common.libs.UrlManager import UrlManager
app.add_template_global(UrlManager.buildStaticUrl,'buildStaticUrl')
app.add_template_global(UrlManager.buildUrl,'buildUrl')
app.add_template_global(UrlManager.buildImageUrl,'buildImageUrl')





