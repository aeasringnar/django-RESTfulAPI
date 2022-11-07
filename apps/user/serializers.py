import os
import sys
import json
import time
import logging
import threading
from uuid import uuid1
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
from .models import *
from .tasks import *


class UserViewsetSerializer(BaseModelSerializer, ModelSerializer):
    
    class Meta:
        model = User
        # exclude = ('deleted', 'is_freeze')
        fields = "__all__"
        read_only_fields = ('id', 'deleted', 'is_freeze', 'sort_timestamp', 'create_timestamp', 'update_timestamp', 'bf_logo_time')


class CreateUserViewsetSerializer(BaseModelSerializer, ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username', 'password', 'mobile', 'email', 'nick_name', 'region', 'avatar_url', 
                  'gender', 'birth_date')


class UpdateUserViewsetSerializer(BaseModelSerializer, ModelSerializer):
    
    class Meta:
        model = User
        fields = ('nick_name', 'region', 'avatar_url', 'gender', 'birth_date')


class ReturnUserViewsetSerializer(BaseModelSerializer, ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('deleted', 'is_freeze', 'bf_logo_time', 'jwt_version')


class OwnerUserViewsetSerializer(BaseModelSerializer, ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('deleted', 'is_freeze', 'password', 'jwt_version')


class AdminLoginSerializer(serializers.Serializer):
    account = serializers.CharField(required=True, max_length=64, label="账号")
    password = serializers.CharField(required=True, max_length=64, label="密码")