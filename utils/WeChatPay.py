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


# 微信统一支付
class WeChatUnityPay(object):
    def __init__(self, out_trade_no, body, total_fee, trade_type, openid):
        """
        :param appid 相应的appid
        :param mch_id 商户号
        :param nonce_str 随机字符串 32位内
        :param sign 签名
        :param body 订单信息或描述
        :param out_trade_no 客户订单编号 32字符内
        :param total_fee 订单金额 单位分
        :param spbill_create_ip 请求用户的ip 终端ip 可以使用 '8.8.8.8'
        :param notify_url 支付通知地址
        :param trade_type = APP 支付类型 小程序和JS支付为 JSAPI app支付为APP
        :param openid: 客户openid JSAPI和小程序支付时必传
        内置参数
        appid = '微信appid'
        AppSecret = '微信AppSecret'
        mch_id = '微信商户id'
        api_key = '微信支付密钥'
        """
        self.api_key = settings.WECHAT_KEY
        self.api_mchid = settings.WECHAT_MCHID
        self.WxPay_request_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信统一下单接口URL
        self.notify_url = settings.WEICHAT_PAY_NOTIFY_URL  # 支付回调地址
        self.error = None
        self.trade_type = trade_type
        self.params = {
            'mch_id': self.api_mchid,
            'nonce_str': get_nonce_str(),
            'body': str(body),
            'out_trade_no': str(out_trade_no),
            'total_fee': str(int(total_fee)),
            'spbill_create_ip': '8.8.8.8',
            'notify_url': self.notify_url
        }
        if trade_type == 'JSAPI':
            self.params['trade_type'] = 'JSAPI'
            self.params['appid'] = settings.WECHAT_MINI_APPID
            self.params['openid'] = openid
        elif trade_type == 'APP':
            self.params['trade_type'] = 'APP'
            self.params['appid'] = settings.WECHAT_APP_APPID
        else:
            self.error = '支付类型丢失'

    def key_value_url(self, value):
        """
        生成键值对：将键值对转为 key1=value1&key2=value2
        """
        string_sign = ''
        for k in sorted(value.keys()):
            string_sign += "{0}={1}&".format(k, value[k])
        # print('键值对：',string_sign)
        return string_sign

    def get_sign(self, params):
        """
        生成 sign 签名
        """
        stringA = self.key_value_url(params)    # 生成键值对
        stringSignTemp = stringA + 'key=' + self.api_key  # APIKEY, API密钥，需要在商户后台设置
        sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()
        params['sign'] = sign

    def get_req_xml(self):
        """
        拼接XML
        """
        self.get_sign(self.params)  # 生成签名
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
        req_xml = self.get_req_xml()
        unifiedorderXML = requests.post(self.WxPay_request_url, data=req_xml)
        unifiedorderXML.encoding ='utf-8'
        unifiedorderXML = unifiedorderXML.text
        print('统一下单接口的返回数据：',unifiedorderXML)
        root = et.fromstring(unifiedorderXML)
        if root.find("result_code").text != 'SUCCESS':
            self.error = "连接微信出错啦！"
            print(self.error)
        prepay_id = root.find("prepay_id").text
        self.params['prepay_id'] = prepay_id
        if self.trade_type == 'JSAPI':
            self.params['package'] = 'prepay_id=%s'%prepay_id   # JSAPI支付场景
        elif self.trade_type == 'APP':
            self.params['package'] = 'Sign=WXPay' # APP支付场景
        self.params['timestamp'] = str(int(time.time()))
        self.params['signType'] = 'MD5'

    def re_finall(self):
        """
        得到prepay_id后再次签名，返回给终端参数
        """
        self.get_prepay_id()
        if self.error:
            print('有错误发生...')
            return None
        if self.trade_type == 'JSAPI':
            # 携带prepay_id再次签名
            sign_again_params = {
                'appId': self.params['appid'],
                'timeStamp': self.params['timestamp'],
                'nonceStr': self.params['nonce_str'],
                'package': self.params['package'],
                'signType': self.params['signType']
            }
            self.get_sign(sign_again_params)
            # 更新签名
            self.params['sign'] = sign_again_params['sign']
            return {
                'appid': self.params['appid'], 
                'mch_id': self.params['mch_id'], 
                'nonce_str': self.params['nonce_str'], 
                'timestamp': self.params['timestamp'], 
                'sign': self.params['sign'], 
                'package': self.params['package'], 
                'signType': self.params['signType']
                }
        elif self.trade_type == 'APP':
            # 再次签名
            sign_again_params = {
               'appid': self.params['appid'],
               'partnerid': self.params['mch_id'],
               'prepayid': self.params['prepay_id'],
               'package': self.params['package'],
               'noncestr': self.params['nonce_str'],
               'timestamp': self.params['timestamp']
            }
            self.get_sign(sign_again_params)
            self.params['sign'] = sign_again_params['sign']
            return {
                'appid': self.params['appid'], 
                'mch_id': self.params['mch_id'], 
                'nonce_str': self.params['nonce_str'], 
                'timestamp': self.params['timestamp'], 
                'sign': self.params['sign'], 
                'package': self.params['package'], 
                'prepay_id': self.params['prepay_id']
                }
        else:
            return None


# 微信企业付款
class WeChatCompanyPay(object):
    def __init__(self, appid, out_trade_no, openid, amount, desc):
         """
        :param appid 商户账号appid 申请商户号的appid或商户号绑定的appid 可变
        :param mch_id 商户号
        :param nonce_str 随机字符串 32位内
        :param sign 签名
        :param partner_trade_no 商户订单号 32字符内
        :param openid: 客户openid 
        :param amount 金额 单位分
        :param desc 企业付款备注
        :param spbill_create_ip 请求用户的ip 终端ip 可以使用 '8.8.8.8'
        :param check_name 校验用户真实姓名选项 NO_CHECK：不校验 FORCE_CHECK：强校验
        """
        self.api_key = settings.WECHAT_KEY
        self.api_mchid = settings.WECHAT_MCHID
        self.pay_url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'  # 微信企业付款接口URL
        self.params = {
            "mch_appid": appid,
            "mchid": self.api_mchid,
            "nonce_str": get_nonce_str(),
            "partner_trade_no": out_trade_no,
            "openid": openid,
            "amount": amount,
            "desc": desc,
            "check_name": 'NO_CHECK',
            "spbill_create_ip": '8.8.8.8'
        }

    def key_value_url(self, value):
        """
        生成键值对：将键值对转为 key1=value1&key2=value2
        """
        string_sign = ''
        for k in sorted(value.keys()):
            string_sign += "{0}={1}&".format(k, value[k])
        return string_sign

    def get_sign(self, params):
        """
        生成 sign 签名
        """
        stringA = self.key_value_url(params)
        stringSignTemp = stringA + 'key=' + self.api_key 
        sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()
        params['sign'] = sign

    def get_req_xml(self):
        """
        拼接XML
        """
        self.get_sign(self.params)  # 生成签名
        xml = "<xml>"
        for k in sorted(self.params.keys()):
            xml += '<{0}>{1}</{0}>'.format(k, self.params[k])
        xml += "</xml>"
        print('得到XML：',xml)
        return xml.encode('utf-8')

    def return_money(self):
        """
        微信企业付款
        """
        
        xml_data = self.get_req_xml()
        cert_path = settings.CERT_PATH
        key_path = settings.CERT_KEY_PATH
        response = requests.post(url=self.pay_url, data=xml_data,cert=(cert_path, key_path)).text
        print('得到返回：', response)
        result = {
            'return_code': ET.XML(response).find('return_code').text,
            'return_msg': ET.XML(response).find('return_msg').text,
            'result_code': ET.XML(response).find('result_code').text if ET.XML(response).find('return_msg') is not None else ''
            }
        return result