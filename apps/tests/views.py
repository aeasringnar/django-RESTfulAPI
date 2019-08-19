
import uuid
import os
import requests
import json
import re
import time
import datetime
import random
import hashlib
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
# from .filters import *
from functools import reduce
from urllib.parse import unquote_plus
'''
serializers 常用字段
name = serializers.CharField(required=False, label='描述', max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
name = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
name = serializers.FloatField(max_value=None, min_value=None)
name = serializers.IntegerField(max_value=None, min_value=None)
name = serializers.DateTimeField(format=api_settings.DATETIME_FORMAT, input_formats=None)
name = serializers.DateField(format=api_settings.DATE_FORMAT, input_formats=None)
name = serializers.BooleanField()
name = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=100))
name = serializers.DictField(child=<A_FIELD_INSTANCE>, allow_empty=True)  DictField(child=CharField())
(mixins.CreateModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,generics.GenericAPIView,viewsets.GenericViewSet)
Q(name__icontains=keyword) 内部是like模糊搜索
__gt 大于 
__gte 大于等于
__lt 小于 
__lte 小于等于
__in 在某某范围内
is null / is not null 为空/非空
.exclude(age=10) 查询年龄不为10的数据
'''
                


# 测试父表 ModelViewSet视图
class FtableViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建测试父表
    retrieve:  检索某个测试父表
    update:  更新测试父表
    destroy:  删除测试父表
    list:  获取测试父表列表
    '''
    queryset = Ftable.objects.all().order_by('-updated')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnFtableSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    # search_fields = ('field01', 'field02', 'field03',)
    # filter_fields = ('field01', 'field02', 'field03',)
    ordering_fields = ('updated', 'sort_time', 'created',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action == 'create':
            return AddFtableSerializer
        if self.action == 'update' or self.action == 'partial_update':
            return UpdateFtableSerializer
        return ReturnFtableSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stables = request.data.get('stables')
        print('stables:', stables)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # 创建子表的方法
        f_id = serializer.data.get('id')
        if stables:
            for item in stables:
                item['ftable'] = f_id
                item_ser = AddStableSerializer(data=item)
                if not item_ser.is_valid():
                    return Response({"message": str(item_ser.errors), "errorCode": 1, "data": {}})
                item_ser.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



# 测试子表 ModelViewSet视图
class StableViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建测试子表
    retrieve:  检索某个测试子表
    update:  更新测试子表
    destroy:  删除测试子表
    list:  获取测试子表列表
    '''
    queryset = Stable.objects.all().order_by('-updated')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnStableSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    # search_fields = ('field01', 'field02', 'field03',)
    # filter_fields = ('field01', 'field02', 'field03',)
    ordering_fields = ('updated', 'sort_time', 'created',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action == 'create':
            return AddStableSerializer
        if self.action == 'update' or self.action == 'partial_update':
            return UpdateStableSerializer
        return ReturnStableSerializer

from .tasks import add, say, mul
# from celery.result import AsyncResult

class BeginCelery(APIView):
    # authentication_classes = (JWTAuthentication,)

    def get(self, request):
        '''
        测试开启celery
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            # if not request.auth:
            #     return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            print(789456789)
            # print(add(1,2))
            add.delay(3,5)
            mul_result = mul.delay(3,5)
            say.delay()
            # 返回的是key
            print(mul_result)
            # res=AsyncResult(mul_result)  # 参数为task_id
            print(dir(mul_result))
            print(mul_result.result)
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})