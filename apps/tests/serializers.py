
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator
from base.serializers import BaseModelSerializer
from .models import *
import time
import datetime
                
class StableSerializer(serializers.Serializer):
    name = serializers.CharField()
    desc = serializers.CharField()
# 新增 测试父表 序列化器
class AddFtableSerializer(serializers.ModelSerializer, BaseModelSerializer):
    stables = StableSerializer(many=True)
    class Meta:
        model = Ftable
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
    def validate(self, attrs):
        # 查看前端传来的所有数据
        print('查看attrs:', attrs)
        # 查看前端是否有通过pk检索数据 来做出相应的改变
        print('查看pk:', self.context['view'].kwargs.get('pk'))
        # 在这里可以获取body参数
        print('查看body参数：', self.context['request'].data)
        del attrs['stables']
        return attrs
# 修改 测试父表 序列化器
class UpdateFtableSerializer(serializers.ModelSerializer, BaseModelSerializer):
    class Meta:
        model = Ftable
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
# 返回 测试父表 序列化器
class ReturnFtableSerializer(serializers.ModelSerializer, BaseModelSerializer):
    class Meta:
        model = Ftable
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
                


# 新增 测试子表 序列化器
class AddStableSerializer(serializers.ModelSerializer, BaseModelSerializer):
    class Meta:
        model = Stable
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
# 修改 测试子表 序列化器
class UpdateStableSerializer(serializers.ModelSerializer, BaseModelSerializer):
    class Meta:
        model = Stable
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
# 返回 测试子表 序列化器
class ReturnStableSerializer(serializers.ModelSerializer, BaseModelSerializer):
    class Meta:
        model = Stable
        exclude = ('deleted',) # or fields = '__all__' or fields = ['field01','field01',]
        # read_only_fields = ('field01', )
                