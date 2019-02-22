from werkzeug.utils import secure_filename
from application import app
from common.libs.Helper import getCurrentDate
import os,stat,uuid

class UploadService():
    @staticmethod
    def uploadByFile(file):
        # 也需要定义resp用于返回信息
        config_upload = app.config['UPLOAD']
        resp = {'code':200,'msg':'操作成功',"data":{}}
        # 通过安全的方式获取文件名,但这里这个方法行不通
        # filename = secure_filename(file.filename)
        filename = file.filename
        app.logger.info(filename)
        # 以第一个点进行切割,取后面的值
        ext = filename.rsplit('.',1)[1]
        if ext not in config_upload['ext']:
            resp['code']= -1
            resp['msg'] = '不允许的扩展类型文件'
            return resp

        # 获取保存图片的路径
        root_path = app.root_path + config_upload['prefix_path']

        # 文件夹的名称
        file_dir = getCurrentDate('%Y%m%d')

        # 最终的保存文件夹的路径
        save_dir = root_path + file_dir

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
            # 让拥有者有777的权限和组用户有读权限,其他用户全部权限
            os.chmod(save_dir,stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)

        # 利用uuid这个模块生成不重复的字符串当成保存的图片名称
        filename = str(uuid.uuid4()).replace('-','') + '.' + ext

        # 保存
        file.save('{0}/{1}'.format(save_dir,filename))
        resp['data'] = {
            'file_key':file_dir + '/' + filename
        }
        return resp


