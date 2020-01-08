from datetime import datetime
from calendar import timegm
import base64, json, re, jwt, os
from django.conf import settings
import requests
import random


class JPush(object):
    def __init__(self):
        self.appkey = settings.JPUSH_APPKEY
        self.secret = settings.JPUSH_SECRET

    def get_token(self):
        tmp = self.appkey + ':' + self.secret
        token = base64.b64encode(tmp.encode('utf-8')).decode('utf-8')
        print('jpush的Token:', token)
        return token

    def push_info(self, receiver, info, all=True):
        '''
        发送信息
        :return:
        '''
        token = self.get_token()
        headers = {
            'Authorization': 'Basic ' + token
        }
        if all:
            data = {
                "platform": "all",
                "audience": "all",
                "notification": {
                    "alert": "{}".format(info)
                }
            }
        else:
            data = {
                "platform": "all",
                "audience": {
                    "alias": ['{}'.format(receiver)]
                },
                "notification": {
                    "alert": "{}".format(info)
                }
            }
        print(data)
        url = 'https://bjapi.push.jiguang.cn/v3/push'
        res = requests.post(url, data=json.dumps(data), headers=headers)
        print('jpush:', res.text)
        return res