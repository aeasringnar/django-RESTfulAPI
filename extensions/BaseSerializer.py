import time
from django.conf import settings
from rest_framework import serializers
from utils.MyDateTime import MyDateTime


class BaseModelSerializer(serializers.Serializer):
    create_time_format = serializers.SerializerMethodField(label="创建时间")
    update_time_format = serializers.SerializerMethodField(label='更新时间')
    
    def get_create_time_format(self, obj):
        return MyDateTime.timestamp_to_str(obj.create_timestamp, settings.REST_FRAMEWORK['DATETIME_FORMAT'])

    def get_update_time_format(self, obj):
        return MyDateTime.timestamp_to_str(obj.update_timestamp, settings.REST_FRAMEWORK['DATETIME_FORMAT'])


class NormalResponseSerializer(serializers.Serializer):
    data = serializers.JSONField(required=True, label="响应数据")
    msg = serializers.CharField(required=True, label="响应描述")
    code = serializers.IntegerField(required=True, label="响应状态码")