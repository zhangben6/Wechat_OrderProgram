import hashlib,base64
import random,string


class UserService():
    @staticmethod
    def geneAuthCode(user_info):
        m = hashlib.md5()
        str = '%s-%s-%s-%s'%(user_info.uid,user_info.login_name,user_info.login_pwd,user_info.login_salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest()

    @staticmethod
    def genePwd(pwd,salt):
        m = hashlib.md5()
        str = '%s-%s'%(base64.encodebytes(pwd.encode('utf-8')),salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest()

    # 生成login_salt的方法
    @staticmethod
    def geneSalt(length=16):
        # string全部的ASC码字符串 + string的数字 = 一个新字符串
        keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
        return (''.join(keylist))



