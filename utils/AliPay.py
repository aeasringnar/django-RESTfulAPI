from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode, decodebytes, encodebytes
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from django.conf import settings
import datetime
import json


class AliPay(object):
    """
    支付宝支付接口
    """

    def __init__(self, method):
        self.appid = settings.ALIPAY_APPID
        self.app_private_key_path = settings.PRIVATE_KEY_PATH
        self.alipay_public_key_path = settings.ALIPUB_KEY_PATH # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        self.app_notify_url = settings.ALIPAY_NOTIFY_URL
        self.app_private_key = None
        self.alipay_public_key = None
        self.method = method
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())

    def direct_pay(self, subject, out_trade_no, total_amount, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": 'QUICK_MSECURITY_PAY'
        }

        biz_content.update(kwargs)
        data = self.build_body(biz_content)
        return self.sign_data(data)

    def ali_auth(self, grant_type, code, refresh_token=None, **kwargs):
        biz_content = {
            "grant_type": grant_type,
            "code": code,
            # "refresh_token": refresh_token,
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body(biz_content)
        return self.sign_data(data)

    def build_body(self, biz_content):
        data = {
            "app_id": self.appid,
            "method": self.method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.app_notify_url,
            "biz_content": biz_content
        }
        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        # ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        print('验证签名', message)
        print('sign', signature)
        return self._verify(message, signature)