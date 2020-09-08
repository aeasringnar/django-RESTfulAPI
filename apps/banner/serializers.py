
import re, emoji
import time
import datetime
from decimal import Decimal
from datetime import timedelta
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.conf import settings
from django.db.models import Q, F
from users.models import *
from public.serializers import BaseSerializer
from .models import *
from django.db import transaction
                


# 新增 轮播图 序列化器
class AddBannerSerializer(serializers.ModelSerializer, BaseSerializer):
    class Meta:
        model = Banner
        fields = '__all__' # or exclude = ('deleted',) or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
# 修改 轮播图 序列化器
class UpdateBannerSerializer(serializers.ModelSerializer, BaseSerializer):
    class Meta:
        model = Banner
        fields = '__all__' # or exclude = ('deleted',) or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
# 返回 轮播图 序列化器
class ReturnBannerSerializer(serializers.ModelSerializer, BaseSerializer):
    class Meta:
        model = Banner
        fields = '__all__' # or exclude = ('deleted',) or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
                