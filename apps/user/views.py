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
    # authentication_classes = (JwtAuthentication, )
    # permission_classes = (AllowAny, )
    # throttle_classes = (VisitThrottle, )
    # filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    # search_fields = ('name', 'desc') # 注意 要针对有索引的字段进行搜索
    # filter_fields = ('status', )
    # ordering_fields = ('id', 'create_timestamp', 'update_timestamp', 'sort_timestamp')
    # pagination_class = Pagination
    
    # 测试对Swagger的指定备注
    @swagger_auto_schema(operation_description="创建用户", operation_summary="创建用户")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)