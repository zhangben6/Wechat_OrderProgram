'''
封装微信付款的api接口函数
'''
import hashlib,requests,uuid
import xml.etree.ElementTree as ET
from application import app,db
from common.models.pay.OauthAccessToken import OauthAccessToken
from common.libs.Helper import getCurrentDate
from common.libs.pay.PayService import PayService
import time,json,datetime

class WeChatService():
    def __init__(self,merchant_key=None):
        self.merchant_key = merchant_key

    # 获取签名信息(算法随机生成的字符串)
    def create_sign(self,pay_data):
        '''
        生产签名 sign
        '''
        stringA = "&".join( ['{0}={1}'.format(k,pay_data.get(k)) for k in sorted(pay_data)] )
        stringSignTemp = '{0}&key={1}'.format(stringA,self.merchant_key)
        sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest()
        return sign.upper()



    # 获取下单信息

    # 假设传送的参数如下：
    # appid：wxd930ea5d5a258f4f
    # mch_id：10000100
    # device_info：1000
    # body：test
    # nonce_str：ibuaiVcKdpRxkhJA

    def get_pay_info(self,pay_data = None):
        '''
        获取支付信息
        '''

        # 生成签名
        sign = self.create_sign(pay_data)

        # 把得到的签名放进去pay_data
        pay_data['sign'] = sign

        # 将这些要发送的信息转换成XML的信息
        xml_data = self.dict_to_xml(pay_data)

        # post提交数据
        headers = {
            'Content-Type':'application/xml'
        }
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        r = requests.post(url=url,data=xml_data.encode('utf-8'),headers=headers)
        r.encoding = 'utf-8'
        app.logger.info(r.text)
        # ***************************************** 卡壳

        # 将这些数据返回给小程序,再发送网络请求,获取支付窗口,注意回调信息的地址是否填写无误
        if r.status_code == 200:
            prepay_id = self.xml_to_dict(r.text).get('prepay_id')
            pay_sign_data = {
                'appId':pay_data.get('appid'),
                'timeStamp':pay_data.get('out_trade_no'),
                'nonceStr':pay_data.get('nonce_str'),
                'package':'prepay_id={0}'.format(prepay_id),
                'signType':'MD5'
            }


            # 前端微信调用支付窗口也要生成一个签名,且需要appid的信息
            pay_sign = self.create_sign(pay_sign_data)
            pay_sign_data.pop('appId')
            pay_sign_data['paySign'] = pay_sign
            pay_sign_data['prepay_id'] = prepay_id # 这个字段前台以后要用到

            app.logger.info(pay_sign_data)
            return pay_sign_data

        return False


    def dict_to_xml(self,dict_data):
        xml = ["<xml>"]
        for k,v in dict_data.items():
            xml.append("<{0}>{1}</{0}>".format(k,v))
        xml.append("</xml>")

        return "".join(xml)

    # 下完单之后,微信的回调数据也是xml形式,需要转换为字典格式的数据
    def xml_to_dict(self,xml_data):
        xml_dict = {}
        # 得到一个根节点
        root = ET.fromstring(xml_data)
        for child in root:
            xml_dict[child.tag] = child.text

        return xml_dict

    # 产生随机字符串
    def get_nonce_str(self):
        return str( uuid.uuid4() ).replace('-','')


    # post发送模板消息的时候,需要用到ACCESS TOKEN
    # 此方法用于获取access token
    def getAccessToken(self):
        token = None

        # 先查询是否有未过期的access_token
        token_info = OauthAccessToken.query.filter(OauthAccessToken.expired_time >= getCurrentDate()).first()
        if token_info:
            token = token_info.access_token
            return token
        config_mina = app.config['MINA_APP']
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(config_mina['appid'],config_mina['appkey'])

        # get请求方式获取Access token
        r = requests.get(url=url)
        if r.status_code != 200 or not r.text:
            return token

        # 开发者文档此处的返回值是json格式数据
        data = json.loads(r.text)

        #　到期时间对应的时间戳(expires_in = 7200)
        now = datetime.datetime.now()
        date = now + datetime.timedelta(seconds=data['expires_in']-200)
        # 存取获取到的access_token到数据库
        model_token = OauthAccessToken()
        model_token.access_token = data['access_token']
        # 设置过期时间
        model_token.expired_time = date.strftime("%Y-%m-%d %H:%M:%S")
        model_token.created_time = getCurrentDate()
        db.session.add(model_token)
        db.session.commit()

        return data['access_token']




























