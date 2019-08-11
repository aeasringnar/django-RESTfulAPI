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
from utils.permissions import JWTAuthPermission,AllowAllPermission, BaseAuthPermission
from .models import *
from .serializers import *
from .filters import *
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


class UploadFile(APIView):
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        '''
        上传文件接口
        '''
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            file_i = request.FILES.items()
            # 这里面filename是用户上传的文件的key upfile是用户上传的文件名
            allow_file_size = 1024 * 1024 * 64
            file_check = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'zip', 'rar', 'xls', 'xlsx', 'doc', 'docx', 'pptx', 'ppt', 'txt']
            is_file = False
            up_files = []
            for key_name, up_file in file_i:
                file_up = TmpFile()
                is_file = True
                print(key_name, up_file.name, up_file.size, up_file.read)
                file_name = up_file.name
                file_size = up_file.size
                check_file = file_name.split('.')[-1]
                new_file_name = str(uuid.uuid1())
                if check_file.lower() not in file_check:
                    json_data['message'] = file_name + '不是规定的文件类型'
                    json_data['errorCode'] = 4
                    return Response(json_data)
                if file_size > allow_file_size:
                    json_data['message'] = file_name + '文件超过64mb，无法上传'
                    json_data['errorCode'] = 4
                    return Response(json_data)
                file_up.name = new_file_name
                request.FILES[key_name].name = new_file_name + '.' + check_file
                file_up.url = request.FILES[key_name]
                file_up.save()
                print(file_up.url)
                # print(dir(file_up.url))
                my_need_url = unquote_plus(str(file_up.url.url))
                if my_need_url[:5] != 'https':
                    my_need_list = my_need_url.split(":")
                    my_need_url = 'https:' + my_need_list[1]
                print(my_need_url)
                up_files.append(my_need_url)
            json_data['data'] = up_files
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({"message": "未知错误", "errorCode": 1, "data": {}})


class Tests(APIView):

    def get(self, request):
        '''
        测试接口
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})
