import time
from django.conf import settings
from rest_framework import serializers
from utils.MyDateTime import MyDateTime


class BaseModelSerializer(serializers.Serializer):
    create_time_format = serializers.SerializerMethodField(label="创建时间")
    update_time_format = serializers.SerializerMethodField(label='更新时间')
    
    def get_create_time_format(self, obj):
        return MyDateTime.timestamp_str(obj.create_timestamp, settings.REST_FRAMEWORK['DATETIME_FORMAT'])

    def get_update_time_format(self, obj):
        return MyDateTime.timestamp_str(obj.update_timestamp, settings.REST_FRAMEWORK['DATETIME_FORMAT'])