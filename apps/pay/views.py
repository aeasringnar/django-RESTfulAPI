import uuid
import os
import requests
import json
import re
import time
import datetime
import random
import hashlib
from xml.etree import ElementTree as et
from django.conf import settings
import hmac
import xml
from django.db.models import F, Q
from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# 官方JWT
# from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler ,jwt_response_payload_handler
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
# 缓存配置
from django.core.cache import cache
# 自定义的JWT配置 公共插件
from utils.utils import jwt_decode_handler,jwt_encode_handler,jwt_payload_handler,jwt_payload_handler,jwt_response_payload_handler,google_otp,VisitThrottle,getDistance,NormalObj
from utils.jwtAuth import JWTAuthentication
from utils.pagination import Pagination
from utils.permissions import JWTAuthPermission, AllowAllPermission, BaseAuthPermission
from .models import *
from .serializers import *
from .filters import *
from functools import reduce
from urllib.parse import unquote_plus
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def wx_notify_url(request):
    '''
    微信支付回调接口
    无需登录便可访问
    无需参数
    '''
    try:
        print('请求方法：',request.method)
        return_xml = """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""
        webData = request.body
        print('回调返回信息：',webData)
        if bool(webData):
            xmlData = ET.fromstring(webData)
            if xmlData.find('return_code').text != 'SUCCESS':
                print('回调出现错误')
                return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
                # print('错误原因：%s' % xmlData.find('return_msg').text)
                # return Response(return_xml)
            else:
                if xmlData.find('result_code').text != 'SUCCESS':
                    print('支付失败！')
                    return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
                else:
                    order_num = xmlData.find('out_trade_no').text
                    good_order = GoodOrder.objects.filter(order_num=order_num).first()
                    service_order = ServiceOrder.objects.filter(order_num=order_num).first()
                    print('查询得到的数据为：',good_order,service_order)
                    if good_order and not service_order:
                        goods = OrderGood.objects.filter(order_id=good_order.id)
                        good_order.status = 1
                        good_order.save()
                        date_str = str(datetime.datetime.now().date())
                        add_jc(date_str,0,good_order)
                        add_jc_m(date_str,0,goods)
                        add_log('付款了ID为%d的商品订单。' % good_order.id,good_order.user.id)
                    elif not good_order and service_order:
                        service_order.status = 1
                        service_order.save()
                        add_log('付款了ID为%d的服务订单。' % service_order.id,service_order.user.id)
                    return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
        return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
    except Exception as e:
        print(e)
        print({"message": "网络错误：%s"%str(e), "errorCode": 1, "data": {}})
        return_xml = """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""
        return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')



class WxPayViewSerializer(serializers.Serializer):
    order_num = serializers.CharField() # 订单编号
    order_info = serializers.CharField() # 订单信息
    total_fee = serializers.FloatField() # 订单金额
class WxPayView(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    serializer_class = WxPayViewSerializer
    def post(self,request):
        '''
        微信支付接口
        '''
        request_log(request)
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            print('openid:', request.user.open_id)
            if request.user.open_id == '' or request.user.open_id == None:
                return Response({"message": "用户openid不能为空", "errorCode": 3, "data": {}})
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            wxpay_object = WeChatPay(out_trade_no='order_num',body='测试',total_fee=1,openid='openid')
            params = wxpay_object.re_finall()
            print('最终得到返回给前端的参数：',params)
            json_data['data'] = params
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({"message": "网络错误：%s"%str(e), "errorCode": 1, "data": {}})