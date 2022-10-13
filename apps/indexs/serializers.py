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
from drf_haystack.serializers import HaystackSerializer
from .search_indexes import UserIndex
from .models import *
# from .tasks import *


class SearchCollectionAndSpotGoodSerializer(HaystackSerializer):
    model_type = SerializerMethodField()
    
    class Meta:
    	# 指定要索引的index方法，在上面建立好的
        index_classes = [ UserIndex ]
        # 指定哪些字段可以被搜索
        fields = [
            "username", "id"
        ]
        search_fields = ["text"]
    
    # def get_model_type(self, obj):
    #     models = [
    #         (Collection, 'collection'),
    #         (SpotGood, 'spotgood'),
    #         (User, 'user'),
    #         (Nft, 'nft'),
    #     ]
    #     for m in models:
    #         if obj.model is m[0]:
    #             return m[1]
    #     return None
