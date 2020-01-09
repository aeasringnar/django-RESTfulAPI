import base64, json, re, jwt, datetime, time
from calendar import timegm
from .settings import api_settings
# 导入谷歌验证码相关模块
import pyotp
# 导入使用缓存的模块
from django.core.cache import cache
import hashlib
import random
import datetime
import time
import math
import requests


# 微信小程序登录方法
def wechat_mini_login(code):
    appid = settings.WECHAT_APPID
    secret = settings.WECHAT_SECRET
    get_user_url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(appid, secret, code)
    response = requests.get(url=get_user_url)
    print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = eval(response.text)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    return response_dic.get('openid'), response_dic.get('unionid'), response_dic.get('session_key')

# 获取微信 access_token
def get_wechat_token():
    appid = settings.MINI_WEIXIN_APP_APPID
    secret = settings.MINI_WEIXIN_APP_SECRET
    get_user_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(appid, secret)
    response = requests.get(url=get_user_url)
    # print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = eval(response.text)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    return response_dic.get('access_token')

# 微信APP登录
def wechat_app_login(code):
    appid = settings.WEIXIN_APP_APPID
    secret = settings.WEIXIN_APP_SECRET
    get_user_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code'.format(appid, secret, code)
    response = requests.get(url=get_user_url)
    print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = eval(response.text)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    access_token = response_dic.get('access_token')
    # refresh_token = response_dic.get('refresh_token')
    open_id = response_dic.get('openid')
    get_user_info = 'https://api.weixin.qq.com/sns/userinfo?access_token={}&openid={}&lang=zh_CN'.format(access_token, open_id)
    response = requests.get(url=get_user_info)
    print('msg：',eval(response.text), type(eval(response.text)))
    response_dic = json.loads(response.text.encode('iso-8859-1').decode('utf8'))
    print('userinfo：', response_dic)
    if response_dic.get('errcode') and response_dic.get('errcode') != 0:
        return {"message": "微信端推送错误：%s,errcode=%s" % (response_dic.get('errmsg'), response_dic.get('errcode')), "errorCode": 1, "data": {}}
    return response_dic


def jwt_payload_handler(account):
    payload = {
        'id': account.pk,
        'exp': datetime.datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA  # 过期时间
    }
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.datetime.utcnow().utctimetuple()
        )
    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE
    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER
    return payload




def jwt_get_user_id_from_payload_handler(payload):
    return payload.get('id')



 
def jwt_encode_handler(payload):
    return jwt.encode(
        payload,
        api_settings.JWT_PRIVATE_KEY or api_settings.JWT_SECRET_KEY,
        api_settings.JWT_ALGORITHM
    ).decode('utf-8')




def jwt_decode_handler(token):
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }
    return jwt.decode(
        token,
        api_settings.JWT_PUBLIC_KEY or api_settings.JWT_SECRET_KEY,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM]
    )




def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token
    }




# google验证模块，必须设置对应的key，才可以操作
def google_otp(pin):
    nowtime = int(time.time())
    totp = pyotp.TOTP(api_settings.GOOGLE_AUTH_ADMIN)
    #totp.verify(pin, nowtime, 5)
    return totp.verify(pin, nowtime, 5)




# 频率组件
from rest_framework.throttling import BaseThrottle
VISIT_RECORD = {}
class VisitThrottle(BaseThrottle):
    def __init__(self):
        self.history = None

    def allow_request(self,request,view):
        remote_addr = request.META.get('HTTP_X_REAL_IP')
        # print('请求的IP：',remote_addr)
        ctime = time.time()
        if remote_addr not in VISIT_RECORD:
            VISIT_RECORD[remote_addr] = [ctime,]
            return True
        history = VISIT_RECORD.get(remote_addr)
        self.history = history
        while history and history[-1] < ctime - 60:
            history.pop()
        if len(history) < 100:  # 限制的频数 设置同一IP该接口一分钟内只能被访问100次
            history.insert(0, ctime)
            return True
        else:
            return False

    def wait(self):
        ctime = time.time()
        return 60 - (ctime-self.history[-1])




# 公共类
class NormalObj(object):

    def create_password(self, password):
        # 生成加密密码 参数：password
        h = hashlib.sha256()
        h.update(bytes(password, encoding='utf-8'))
        h_result = h.hexdigest()
        return h_result

    def create_code(self):
        # 生成随机验证码
        base_str = '0123456789qwerrtyuioplkjhgfdsazxcvbnm'
        return ''.join(random.sample(base_str, 6))

    def create_order(self, order_type):
        # 生成订单编号 参数订单类型：order_type
        now_date_time_str = str(
            datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
        base_str = '01234567890123456789'
        random_num = ''.join(random.sample(base_str, 6))
        random_num_two = ''.join(random.sample(base_str, 5))
        order_num = now_date_time_str + str(order_type) + random_num + random_num_two
        return order_num


def getDistance(lat1, lng1, lat2, lng2):
    # 计算两经纬度之间的距离 返回距离单位为公里
    radLat1 = (lat1 * math.pi / 180.0)
    radLat2 = (lat2 * math.pi / 180.0)
    a = radLat1 - radLat2
    b = (lng1 * math.pi / 180.0) - (lng2 * math.pi / 180.0)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(math.sin(b/2), 2)))
    s = s * 6378.137
    return s