from flask import Blueprint, g, request,jsonify
from application import app
import json,re
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.Image import Image

route_upload = Blueprint('upload_page',__name__)

@route_upload.route("/ueditor",methods=['GET','POST'])
def ueditor():
    req = request.values
    action = req['action'] if 'action' in req else ''

    # 提示用户可以进行上传图片操作
    if action == 'config':
        root_path = app.root_path
        config_path = '{0}/web/static/plugins/ueditor/upload_config.json'.format(root_path)
        with open(config_path) as fp:
            try:
                config_data  = json.loads(re.sub(r'\/\*.*\*/','',fp.read() ))
            except:
                config_data = {}
        return jsonify(config_data)

    # 本地图片上传及显示处理函数
    if action == 'uploadimage':
        return uploadImage()

    # 用户可以在线管理图片,返回本地上传的所有图片(将图片数据存储到数据库)
    if action == 'listimage':
        return listImage()


    return 'upload'

def uploadImage():
    resp = {'state':'SUCCESS','url':'','title':'','original':''}
    file_target = request.files
    upfile = file_target['upfile'] if 'upfile' in file_target else ''
    if upfile is None:
        resp['status'] = '上传失败'
        return jsonify(resp)
    # 上传文件的操作,使用统一封装好的类
    ret = UploadService.uploadByFile(upfile)
    if ret['code'] != 200:
        resp['state'] = '上传失败' + ret['msg']
        return jsonify(resp)

    # 设置返回图片的url地址
    resp['url'] = UrlManager.buildImageUrl(ret['data']['file_key'])
    return jsonify(resp)

def listImage():
    resp = {'state':'SUCCESS','list':{},'start':0,'total':0}
    req = request.values
    start = int(req['start']) if 'start' in req else 0
    page_size = int(req['size']) if 'size' in req else 20

    query = Image.query
    if start > 0:
        query = query.filter(Image.id < start)

    # 用倒序方式求出list  根据偏移参数和页面大小参数
    list = query.order_by(Image.id.desc()).limit(page_size).all()
    images = []
    if list:
        for item in list:
            images.append({'url':UrlManager.buildImageUrl(item.file_key)})
            start = item.id
    resp['list'] = images
    resp['total'] = len(list)
    resp['start'] = start
    return jsonify(resp)
















