import os
import sys
import json
import time
import logging
import threading
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction
from django.core.cache import caches
from django.db.models import F, Q, Count, Sum, Max, Min
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField, ModelSerializer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from extensions.BaseSerializer import BaseModelSerializer
from .models import ConfDict
# from .tasks import *
from drf_yasg import openapi


class GetAllEnumDataResponse(serializers.Serializer):
    data = serializers.DictField()
    

class NormalResponseSerializer(serializers.Serializer):
    data = serializers.JSONField(required=True, label="返回数据")
    message = serializers.CharField(required=True, label="返回描述")
    errorCode = serializers.CharField(required=True, label="异常错误码")

upload_param = openapi.Parameter(name='file', in_=openapi.IN_FORM, description="上传文件", type=openapi.TYPE_FILE, required=True)
upload_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['file'],
    properties={
        'file': openapi.Schema(type=openapi.TYPE_STRING, description="文件")
    }
)