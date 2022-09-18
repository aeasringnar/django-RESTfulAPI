import json
import os
import sys
import threading
import time
import logging
from uuid import uuid1
from decimal import Decimal
from datetime import datetime, timedelta
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework.utils import model_meta
from django.db.models import F, Q, Count, Sum, Max, Min
from django.db import transaction
from django.core.cache import caches
from django.conf import settings
from extensions.BaseSerializer import BaseModelSerializer
from .models import *
from .tasks import *


class UserViewsetSerializer(BaseModelSerializer, serializers.ModelSerializer):
    
    class Meta:
        model = User
        # exclude = ('deleted', 'is_freeze')
        fields = "__all__"
        read_only_fields = ('id', 'deleted', 'is_freeze', 'sort_timestamp', 'create_timestamp', 'update_timestamp', 'bf_logo_time')


class OwnerUserViewsetSerializer(BaseModelSerializer, serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('deleted', 'is_freeze', 'password', 'jwt_version')


class AdminLoginSerializer(serializers.Serializer):
    account = serializers.CharField(required=True, max_length=64, label="账号")
    password = serializers.CharField(required=True, max_length=64, label="密码")