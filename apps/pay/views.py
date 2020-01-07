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
from utils.WeChatPay import WeChatUnityPay
from utils.AliPay import AliPay



@csrf_exempt
@transaction.atomic
def wechat_notify_url(request):
    '''
    微信支付回调接口
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
            else:
                if xmlData.find('result_code').text != 'SUCCESS':
                    print('支付失败！')
                    return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
                else:
                    print('订单支付成功...准备修改订单状态')
                    order_num = xmlData.find('out_trade_no').text
                    order = Order.objects.filter(order_num=order_num).first()
                    # 更新状态 更新支付时间 更新支付方式
                    order.status = 1
                    order.pay_time = datetime.datetime.now()
                    order.pay_type = 1
                    order.save()
                    # 整理库存和销量，当订单到这里时会将库存锁死
                    for detail in order.order_details.all():
                        detail.good_grade.sales += detail.buy_num
                        detail.good_grade.stock -= detail.buy_num
                        detail.good_grade.save()
                    return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
        return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
    except Exception as e:
        print(e)
        print({"message": "网络错误：%s"%str(e), "errorCode": 1, "data": {}})
        return_xml = """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""
        return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')


class AlipayNotifyUrlView(APIView):
    
    def post(self, request):
        """
        处理支付宝的notify_url
        :param request:
        :return:
        """
        try:
            processed_dict = {}
            for key, value in request.data.items():
                processed_dict[key] = value
            if processed_dict:
                print('支付宝的参数', processed_dict)
                sign = processed_dict.pop("sign", None)
                alipay = AliPay(method='alipay.trade.app.pay')
                verify_re = alipay.verify(processed_dict, sign)
                print('支付宝的参数', processed_dict)
                print('检验参数结果', verify_re)
                out_trade_no = processed_dict.get('out_trade_no', None)
                trade_no = processed_dict.get('trade_no', None)
                # response = VerifyAndDo(out_trade_no, pay_way='alipay')
                order = Order.objects.filter(order_num=out_trade_no, status=0).first()
                if order:
                    order.status = 1
                    order.wechat_order_num = trade_no
                    order.pay_time = datetime.datetime.now()
                    order.pay_type = 2
                    order.save()
                    # 整理库存和销量，当订单到这里时会将库存锁死
                    for detail in order.order_details.all():
                        detail.good_grade.sales += detail.buy_num
                        detail.good_grade.stock -= detail.buy_num
                        detail.good_grade.save()
                else:
                    print('未找到订单编号为：的订单...' % order_num)
            return Response('success')
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


class WxPayViewSerializer(serializers.Serializer):
    order_num = serializers.CharField() # 订单编号
class WeChatPricePayView(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    serializer_class = WxPayViewSerializer
    @transaction.atomic
    def post(self,request):
        '''
        微信支付接口
        '''
        try:
            json_data = {"message": "支付数据返回成功", "errorCode": 0, "data": {}}
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            if request.user.group.group_type in ['SuperAdmin', 'Admin']:
                return Response({"message": "非法用户，无法下单", "errorCode": 2, "data": {}})
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            order_num = serializer.data.get('order_num')
            order = Order.objects.filter(order_num=order_num, status=0).first()
            if not order:
                return Response({"message": '订单未找到，支付失败。', "errorCode": 3, "data": {}})
            order_details = order.order_details.all()
            check_stock = True
            # 使用悲观锁梳理订单并发问题  考虑库存不足时是否将订单设置为失效
            for item in order_details:
                good_grade = GoodGrade.objects.select_for_update().get(id=item.good_grade_id)
                if item.buy_num > good_grade.stock:
                    check_stock = False
                    break
            if not check_stock:
                return Response({"message": '有规格库存不足，无法发起支付。', "errorCode": 3, "data": {}})
            price = int(float(str(order.all_price)) * 100)
            wxpay_object = WeChatUnityPay(out_trade_no=order_num, body='订单' + order_num[12:], total_fee=price, trade_type='JSAPI', openid=request.user.open_id)
            params = wxpay_object.re_finall()
            print('最终得到返回给前端的参数：', params)
            json_data['data'] = params
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})