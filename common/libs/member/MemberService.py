import hashlib,base64
import random,string
from application import app
import requests,json


class MemberService():
    @staticmethod
    def geneAuthCode(member_info):
        m = hashlib.md5()
        str = '%s-%s-%s'%(member_info.id,member_info.salt,member_info.status)
        m.update(str.encode('utf-8'))
        return m.hexdigest()



    # 生成login_salt的方法
    @staticmethod
    def geneSalt(length=16):
        # string全部的ASC码字符串 + string的数字 = 一个新字符串
        keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
        return (''.join(keylist))

    @staticmethod
    def getWechatOpenid(code):
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code' \
            .format(app.config['MINA_APP']['appid'], app.config['MINA_APP']['appkey'], code)
        r = requests.get(url)
        res = json.loads(r.text)
        openid = None
        if 'openid' in res:
            openid = res['openid']
        return openid




