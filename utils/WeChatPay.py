from django.conf import settings
import re
import hashlib
import json
import hmac
import requests
from xml.etree import ElementTree as et


def get_nonce_str():
    base_str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    random_str = ''.join(random.sample(base_str, 32))
    return random_str


class WeChatJSAPIPay(object):
    def __init__(self, order_num, body, total_fee, nonce_str, openid):
        """
        :param order_num: 订单编号 32字符内
        :param body: 订单信息
        :param total_fee: 订单金额 #单位为分
        :param nonce_str: 32位内随机字符串
        :param spbill_create_ip: 客户端请求IP地址
        :param openid: 客户openid
        appid = '微信appid'
        AppSecret = '微信AppSecret'
        mch_id = '微信商户id'
        api_key = '微信支付密钥'
        spbill_create_ip = '8.8.8.8' # 用户请求地址 终端IP 调用微信支付API的机器IP
        """
        self.api_key = settings.WEICHAT_PAY_API_KEY
        self.params = {
            'appid': settings.WEICHAT_PAY_APPID,
            'mch_id': settings.WEICHAT_PAY_MCHID,
            'nonce_str': nonce_str,
            'openid': openid,
            'body': str(body),
            'out_trade_no': str(order_num),
            'total_fee': str(int(total_fee)),
            'spbill_create_ip': '8.8.8.8',
            'trade_type': 'JSAPI',
            'notify_url': 'https://www.your.com/wxnotifyurl',# 支付回调地址
        }

        self.WxPay_request_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信请求url
        self.error = None

    def key_value_url(self, value):
        """
        将将键值对转为 key1=value1&key2=value2
        """
        string_sign = ''
        for k in sorted(value.keys()):
            string_sign += "{0}={1}&".format(k, value[k])
        # print('键值对：',string_sign)
        return string_sign

    def get_sign(self, params):
        """
        生成sign 签名
        """
        stringA = self.key_value_url(params)
        stringSignTemp = stringA + 'key=' + self.api_key  # APIKEY, API密钥，需要在商户后台设置
        # print('最终键值对：',stringSignTemp)
        # sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()
        sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()
        # k = hashlib.sha256()
        # k.update(sign.encode())
        # j = hmac.new(sign.encode(), digestmod=hashlib.sha256)
        # print(j.hexdigest().upper())
        # print(k.hexdigest().upper())
        # sign = j.hexdigest().upper()
        # print('生成签名sign：',sign)
        params['sign'] = sign

    def get_req_xml(self):
        """
        拼接XML
        """
        self.get_sign(self.params)
        xml = "<xml>"
        for k in sorted(self.params.keys()):
            xml += '<{0}>{1}</{0}>'.format(k, self.params[k])
        xml += "</xml>"
        print('得到XML：',xml)
        return xml.encode('utf-8')

    def get_prepay_id(self):
        """
        请求获取prepay_id
        """
        import requests
        from xml.etree import ElementTree as et
        xml = self.get_req_xml()
        # unifiedorderXML = requests.post('https://api.mch.weixin.qq.com/pay/unifiedorder', data=xml)
        unifiedorderXML = requests.post(self.WxPay_request_url, data=xml)
        unifiedorderXML.encoding ='utf-8'
        unifiedorderXML = unifiedorderXML.text
        print('统一下单接口的返回数据：',unifiedorderXML)
        # tree = et.parse(unifiedorderXML)
        # root = tree.getroot()
        root = et.fromstring(unifiedorderXML)
        if root.find("result_code").text != 'SUCCESS':
            self.error = "连接微信出错啦！"
            print(self.error)
        prepay_id = root.find("prepay_id").text
        self.params['prepay_id'] = prepay_id
        # self.params['package'] = 'Sign=WXPay' # APP支付场景
        self.params['package'] = 'prepay_id=%s'%prepay_id   # JSAPI支付场景
        self.params['timestamp'] = str(int(time.time()))
        self.params['signType'] = 'MD5'

    def re_finall(self):
        """
        得到prepay_id后再次签名，返回给终端参数
        """
        self.get_prepay_id()
        if self.error:
            print('有错误发生')
            return 
        sign_again_params = {
            'appId': self.params['appid'],
            'timeStamp': self.params['timestamp'],
            'nonceStr': self.params['nonce_str'],
            'package': self.params['package'],
            'signType': self.params['signType']
        }
        self.get_sign(sign_again_params)
        self.params['sign'] = sign_again_params['sign']

        # 移除其他不需要返回参数
        # print('最后一步:', self.params)
        parms_keys = []
        for i in self.params.keys():
            parms_keys.append(i)
        for i in parms_keys:
            if i not in ['appid', 'mch_id', 'nonce_str', 'timestamp', 'sign', 'package', 'signType']:
                self.params.pop(i)
        # print('传给前端的parms:', self.params)
        return self.params