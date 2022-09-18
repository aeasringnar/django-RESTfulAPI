import json
import os
import sys
import threading
import time
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from django.db.models import F, Q, Count, Sum, Max, Min
from django.db import transaction
from django.core.cache import caches
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.forms.models import model_to_dict
from django.http.response import HttpResponseNotFound
from drf_yasg.utils import swagger_auto_schema
from extensions.Pagination import Pagination
from extensions.Throttle import VisitThrottle
from extensions.JwtAuth import JwtAuthentication
from extensions.Permission import IsAuthPermission
from extensions.MyResponse import MyJsonResponse
from extensions.JwtToken import JwtToken
from .models import *
from .serializers import *
from .tasks import *
# from .filters import *


class UserViewSet(ModelViewSet):
    '''
    更新指定ID的用户，局部更新
    create:  创建用户
    retrieve:  检索指定ID的用户
    update:  更新指定ID的用户
    destroy:  删除指定ID的用户
    list:  获取用户列表
    '''
    queryset = User.objects.filter()
    serializer_class = UserViewsetSerializer
    authentication_classes = (JwtAuthentication, )
    permission_classes = (AllowAny, )
    throttle_classes = (VisitThrottle, )
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name', 'desc') # 注意 要针对有索引的字段进行搜索
    filter_fields = ('status', )
    ordering_fields = ('id', 'create_timestamp', 'update_timestamp', 'sort_timestamp')
    pagination_class = Pagination
    
    # 测试对Swagger的指定备注
    @swagger_auto_schema(operation_description="创建用户", operation_summary="创建用户")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class OwnerUserInfoViewset(mixins.ListModelMixin, GenericViewSet):
    '''
    list:  获取自己的用户信息
    '''
    serializer_class = OwnerUserViewsetSerializer
    authentication_classes = (JwtAuthentication, )
    permission_classes = (IsAuthPermission, )
    throttle_classes = (VisitThrottle, )
    
    def get_queryset(self):
        '''重写get_queryset，用来返回目标用户的数据，因为在token验证那里已经确定了用户是否存在'''
        if self.request.auth:
            return User.objects.filter(id=self.request.user.id)
        return None
    
    def list(self, request, *args, **kwargs):
        '''重写list方法，使接口返回的数据是一个对象而不是数组'''
        instance = User.objects.filter(id=self.request.user.id).first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AdminLoginView(generics.GenericAPIView):
    '''后台登录接口'''
    serializer_class = AdminLoginSerializer
    
    @transaction.atomic
    def post(self, request):
        res = MyJsonResponse()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # 新版验证写法，使异常通过自定义的异常处理器抛出，也不需要在视图函数里捕获异常了，有统一的异常处理器
        username = serializer.data.get("account")
        password = serializer.data.get("password")
        user = User.objects.filter(username=username).first()
        if not user:
            res.update(message="User not found.", errorCode=2)
            return res.data
        if user.password != password:
            res.update(message="Wrong password.", errorCode=2)
            return res.data
        user.jwt_version += 1 
        payload = {
            'id': user.id,
            'jwt_version': user.jwt_version
        }
        logging.debug(payload)
        jwt_token = JwtToken().encode_user(payload)
        user.save()
        res.update(data={'token': jwt_token})
        return res.data


class TestView(APIView):
    def post(self, request):
        logging.info('test' * 3)
        raise ValueError('test error')