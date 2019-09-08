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
# 测试的cache 所用的包 drf-extensions
# from rest_framework_extensions.cache.mixins import CacheResponseMixin # CacheResponseMixin使用在viewset里可以针对某些请求进行缓存
# from rest_framework_extensions.cache.decorators import (
#     cache_response
# )


# 后台登录
class LoginView(generics.GenericAPIView):
    serializer_class = LoginViewSerializer
    def post(self, request):
        '''
        后台登录接口
        '''
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            data = (serializer.data)
            username = data.get('username')
            password = data.get('password')
            user = User.objects.filter(Q(username=username) | Q(phone=username) | Q(email=username)).first()
            if not user:
                return Response({"message": "用户不存在", "errorCode": 2, "data": {}})
            if user.status == '0':
                return Response({"message": "账号被冻结，无法登录。", "errorCode": 2, "data": {}})
            if user.password == password:
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                data = jwt_response_payload_handler(token, user, request)
                user.update_time = datetime.datetime.now()
                user.save()
                return Response({"message": "登录成功", "errorCode": 0, "data": data})
            else:
                return Response({"message": "密码错误", "errorCode": 1, "data": {}})
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 后台用户管理
class UserViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建用户
    retrieve:  检索某个用户
    update:  更新用户
    destroy:  删除用户
    list:  获取用户列表
    '''
    queryset = User.objects.all().order_by('-update_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnUserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('username', 'phone', 'email',)
    # filter_fields = ('start_work_time','end_work_time',)
    ordering_fields = ('update_time', 'sort_time', 'create_time',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AddUserSerializer
        return ReturnUserSerializer


# 测试导出Excel数据流
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
class UserDictExportViewset(XLSXFileMixin, ReadOnlyModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = ReturnUserSerializer
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [BaseAuthPermission, ]
    renderer_classes = (XLSXRenderer,)
    filename = 'my_export.xlsx'
    column_header = {
        'titles': [
            "Column_1_name",
            "Column_2_name",
            "Column_3_name",
        ],
    }


# 获取个人信息
class UserInfo(APIView):
    authentication_classes = (JWTAuthentication,)

    # 测试对返回的数据进行缓存
    # @cache_response()
    def get(self, request, *args, **kwargs):
        '''
        获取个人信息
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            user = User.objects.filter(id=request.user.id).first()
            user.bf_logo_time = user.update_time
            user.save()
            json_data['data'] = ReturnUserSerializer(user).data
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 后台权限接口
class AuthViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建权限
    retrieve:  检索某个权限
    update:  更新权限
    destroy:  删除权限
    list:  获取权限列表
    '''
    queryset = Auth.objects.all().order_by('-update_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnAuthSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('auth_type',)
    ordering_fields = ('update_time', 'sort_time', 'create_time',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AddAuthSerializer
        return ReturnAuthSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 删除权限子表
        auths = AuthPermission.objects.filter(auth_id=instance.id)
        for item in auths:
            item.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)