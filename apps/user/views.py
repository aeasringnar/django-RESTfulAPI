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
from user.permissions import BaseAuthPermission, AllowAllPermission, JWTAuthPermission
# 自定义的JWT配置
from base.utils import *
from base.authentication import JWTAuthentication
from .models import *
from .serializers import *
from .filters import *
from base.pagination import Pagination
from functools import reduce
from urllib.parse import unquote_plus
'''
name = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
name = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
name = serializers.FloatField(max_value=None, min_value=None)
name = serializers.IntegerField(max_value=None, min_value=None)
name = serializers.DateTimeField(format=api_settings.DATETIME_FORMAT, input_formats=None)
name = serializers.DateField(format=api_settings.DATE_FORMAT, input_formats=None)
name = serializers.BooleanField()
name = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=100))
(mixins.CreateModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,GenericViewSet)
Q(name__icontains=keyword)
'''


class LoginView(generics.GenericAPIView):
    serializer_class = LoginViewSerializer
    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            data = (serializer.data)
            username = data.get('username')
            password = data.get('password')
            user = User.objects.filter(Q(username=username) | Q(phone=username) | Q(email=username)).first()
            # user = User.objects.filter(employ__phone=username).first()
            if not user:
                return Response({"message": "用户不存在", "errorCode": 2, "data": {}})
            if user.status == '0':
                return Response({"message": "账号被冻结，无法登录。", "errorCode": 2, "data": {}})
            if user.password == password:
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                data = jwt_response_payload_handler(token, user, request)
                return Response({"message": "登录成功", "errorCode": 0, "data": data})
            else:
                return Response({"message": "密码错误", "errorCode": 1, "data": {}})
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "未知错误：%s" % e, "errorCode": 1, "data": {}})


class UserViewset(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,GenericViewSet):
    '''
    修改局部数据
    create:  创建用户
    retrieve:  检索某个用户
    update:  更新用户
    destroy:  删除用户
    list:  获取用户列表
    '''
    queryset = User.objects.all().order_by('-updated')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnUserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('username', 'phone', 'email',)
    # filter_fields = ('start_work_time','end_work_time',)
    ordering_fields = ('updated', 'sort_time', 'created',)
    pagination_class = Pagination


class UserInfo(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            user = User.objects.filter(id=request.user.id).first()
            user.bf_logo_time = user.updated
            user.save()
            user.updated = datetime.datetime.now()
            user.save()
            serializer_user_data = UserInfoSerializer(user)
            json_data['data'] = serializer_user_data.data
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "未知错误：%s" % e, "errorCode": 1, "data": {}})