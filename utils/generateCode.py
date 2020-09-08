import os

def main(app_list):
    try:
        for data in app_list:
            print('app：',data)
            app_name = data.get('name')
            models = data.get('models')
            print('所有模型：',models)
            app_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'apps'),app_name)
            if os.path.isdir(app_path):
                # 序列化器
                MySerializer = """
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from public.serializers import BaseModelSerializer
from rest_framework.utils import model_meta
import threading
from .models import *
import time
import datetime
from django.db.models import F, Q
from django.db import transaction
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
                """
                # ModelViewSet视图
                MyViewSet = """
import uuid, os, sys, requests, json, re, time, datetime, random, hashlib, hmac, base64, xml, subprocess, threading
from django.db import transaction
from decimal import Decimal
from django.db.models import F, Q
from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.forms.models import model_to_dict
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
from django.conf import settings
from django.forms.models import model_to_dict
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
name = serializers.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name='金额')
(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet, generics.GenericAPIView)
Q(name__icontains=keyword) 内部是like模糊搜索
__gt 大于 
__gte 大于等于
__lt 小于 
__lte 小于等于
__in 在某某范围内
is null / is not null 为空/非空
.exclude(age=10) 查询年龄不为10的数据
'''
                """
                # 写入 urls.py
                url_viewsets = ''
                for model_item in models:
                    name = model_item.get('name')
                    url_viewsets += name + 'Viewset, '
                MyUrls = '''from {app_name}.views import {viewsets}'''.format(app_name=app_name,viewsets=url_viewsets)
                # 生成 基本serializers 序列化器 'serializers.py'
                with open(os.path.join(app_path,'serializers.py'),'w',encoding='utf-8') as f:
                    f.write(MySerializer)
                # 生成 基本ViewSet 视图
                with open(os.path.join(app_path,'views.py'),'w',encoding='utf-8') as f:
                    f.write(MyViewSet)
                # 生成 基本urls 路由
                with open(os.path.join(app_path,'urls.py'),'w',encoding='utf-8') as f:
                    f.write(MyUrls)
                for model_item in models:
                    name = model_item.get('name')
                    verbose = model_item.get('verbose')
                    searchs = model_item.get('searchs')
                    filters = model_item.get('filters')
                    # 序列化器
                    MySerializer = """


# 新增 {verbose} 序列化器
class Add{name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {name}
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
# 修改 {verbose} 序列化器
class Update{name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {name}
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
# 返回 {verbose} 序列化器
class Return{name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {name}
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
                """.format(name=name, verbose=verbose)
                    # ModelViewSet视图
                    MyViewSet = """


# {verbose} ModelViewSet视图
class {name}Viewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建{verbose}
    retrieve:  检索某个{verbose}
    update:  更新{verbose}
    destroy:  删除{verbose}
    list:  获取{verbose}列表
    '''
    queryset = {name}.objects.all().order_by('-create_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = Return{name}Serializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    # search_fields = ({searchs})
    # filter_fields = ({filters})
    ordering_fields = ('id', 'update_time', 'create_time',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ['create']:
            return Add{name}Serializer
        if self.action in ['update', 'partial_update']:
            return Update{name}Serializer
        return Return{name}Serializer

    def get_queryset(self):
        return {name}.objects.all(filter_time=self.request.query_params.get('filter_time')).filter().order_by('-create_time')
        if bool(self.request.auth) and self.request.user.group_id == 1:
            return {name}.objects.all().order_by('-create_time')
        elif bool(self.request.auth):
            return {name}.objects.filter(user_id=self.request.user.id).order_by('-create_time')
        else:
            return {name}.objects.filter(id=0).order_by('-create_time')
                """.format(name=name, verbose=verbose, searchs=searchs, filters=filters)
                    # 路由
                    MyUrl = """
# {verbose}管理
router.register(r'{lower}', {name}Viewset, base_name='{verbose}管理')""".format(name=name, verbose=verbose, lower=name.lower(), app_name=app_name)
                    # 开始自动生成代码
                    # 生成 serializers 序列化器 'serializers.py'
                    with open(os.path.join(app_path,'serializers.py'),'a',encoding='utf-8') as f:
                        f.write(MySerializer)
                    # 生成 ViewSet 视图
                    with open(os.path.join(app_path,'views.py'),'a',encoding='utf-8') as f:
                        f.write(MyViewSet)
                    # 生成 path 路由
                    with open(os.path.join(app_path,'urls.py'),'a',encoding='utf-8') as f:
                        f.write(MyUrl)
                    print("%s生成完毕！"%name)
                print("app：%s 生成完毕！"%app_name)
            else:
                print('app：%s 不存在...' % app_name)
    except Exception as e:
        print("代码生成过程出错...错误原因：%s" % str(e))


if __name__ == '__main__':
    # 自动生成代码，将表内容按照格式放入，使用Python脚本运行即可
    # 存放 app名称、模型以及表名
    # 示例：app_list = [{'name': 'tests','models': [{'name':'Group','verbose':'用户组表','searchs':"'field1', ",'filters':"'field1', "},{'name':'User','verbose':'用户表'}]}]
    app_list = [
        {'name': 'tests','models': [
            {'name':'Ftable','verbose':'测试父表','searchs':"",'filters':""},
            {'name':'Stable','verbose':'测试子表','searchs':"'field1', ",'filters':"'field1', "},
            ]
        },
        ]
    app_list = []
    main(app_list)