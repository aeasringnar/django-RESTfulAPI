from rest_framework import serializers
from django.conf import settings
import time
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
Q(name__icontains=keyword) 内部是like模糊搜索
__gt 大于 
__gte 大于等于
__lt 小于 
__lte 小于等于
__in 在某某范围内
is null / is not null 为空/非空
.exclude(age=10) 查询年龄不为10的数据
'''


class BaseModelSerializer(serializers.Serializer):
    create_time_format = serializers.SerializerMethodField(label="创建时间")
    update_time_format = serializers.SerializerMethodField(label='更新时间')
    
    def get_create_time_format(self, obj):
        return time.strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'], time.localtime(obj.create_timestamp / 1000))

    def get_update_time_format(self, obj):
        return time.strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'], time.localtime(obj.update_timestamp / 1000))