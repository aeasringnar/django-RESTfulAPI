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
from django.db.models import F, Q, Count, Sum, Max, Min
from django.db import transaction
from django.core.cache import caches
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.forms.models import model_to_dict
from django.http.response import HttpResponseNotFound
from .models import *
from .serializers import *
from .tasks import *
# from .filters import *


class UserViewSet(ModelViewSet):
    '''
    更新指定ID的用户
    create:  创建用户
    retrieve:  检索指定ID的用户
    update:  更新指定ID的用户
    destroy:  删除指定ID的用户
    list:  获取用户列表
    '''
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = [JWTAuthPermission, ]
    # throttle_classes = [VisitThrottle]
    serializer_class = UserViewsetSerializer
    # filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    # search_fields = ('name', 'desc')
    # filter_fields = ('address', 'user', 'status',)
    # ordering_fields = ('id', 'update_time', 'create_time',)
    # pagination_class = Pagination