'''
封装微信付款的api接口函数
'''
import hashlib,requests,uuid
import xml.etree.ElementTree as ET
from application import app


class WeChatService():
    def __init__(self,merchant_key=None):
        self.merchant_key = merchant_key

    # 获取签名信息(算法随机生成的字符串)
    def create_sign(self,pay_data):
        '''
        生产签名
        '''
        stringA = "&".join( ['{0}={1}'.format(k,pay_data.get(k)) for k in sorted(pay_data)] )
        stringSignTemp = '{0}&key={1}'.format(stringA,self.merchant_key)
        sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest()
        return sign.upper()



    # 获取下单信息
    def get_pay_info(self,pay_data = None):
        '''
        获取支付信息
        '''
        sign = self.create_sign(pay_data)
        pay_data['sign'] = sign
        xml_data = self.dict_to_xml(pay_data)
        app.logger.info('阿达发送发',xml_data)
        headers = {
            'Content-Type':'application/xml'
        }
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        r = requests.post(url=url,data=xml_data.encode('utf-8'),headers=headers)
        r.encoding = 'utf-8'
        # ***************************************** 卡壳
        if r.status_code == 200:
            prepay_id = self.xml_to_dict(r.text).get('prepay_id')
            pay_sign_data = {
                'appId':pay_data.get('appid'),
                'timeStamp':pay_data.get('out_trade_no'),
                'nonceStr':pay_data.get('nonceStr'),
                'package':'prepay_id={0}'.format(prepay_id),
                'signType':'MD5'
            }
            pay_sign = self.create_sign(pay_sign_data)
            pay_sign_data.pop('addId')
            pay_sign_data['paySign'] = pay_sign
            pay_sign_data['prepay_id'] = prepay_id

            return pay_sign_data

        return False

    def dict_to_xml(self,dict_data):
        xml = ["<xml>"]
        for k,v in dict_data.items():
            xml.append("<{0}>{1}</{0}>".format(k,v))
        xml.append("</xml>")

        return "".join(xml)


    def xml_to_dict(self,xml_data):
        xml_dict = {}
        # 得到一个根节点
        root = ET.fromstring(xml_data)
        for child in root:
            xml_dict[child.tag] = child.text

        return xml_dict

    def get_nonce_str(self):
        return str(uuid.uuid4()).replace('-','')


