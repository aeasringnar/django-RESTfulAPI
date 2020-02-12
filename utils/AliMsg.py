from datetime import datetime
from calendar import timegm
import base64, json, re, jwt, oss2, os
from django.conf import settings
import requests
import random
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


def create_code():
    # 生成随机验证码
    base_str = '01234567890123456789'
    return ''.join(random.sample(base_str, 4))


# 阿里短信 
class SendSmsObject(object):
    def __init__(self, key, serect, region, name):
        self.key = key
        self.serect = serect
        self.region = region
        self.name = name

    def get_template_param(self, **kwargs):
        return json.dumps(kwargs)

    def send_code(self, code_temp, mobile, code):
        client = AcsClient(self.key, self.serect, self.region)
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', self.region)
        request.add_query_param('SignName', self.name)
        request.add_query_param('TemplateCode', code_temp)
        request.add_query_param('PhoneNumbers', mobile)
        request.add_query_param('TemplateParam', self.get_template_param(code=code))
        response = client.do_action(request)
        return json.loads(response.decode('utf-8'))