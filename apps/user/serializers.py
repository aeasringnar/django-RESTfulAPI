from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator
from base.serializers import BaseModelSerializer
from .models import *
import time
import datetime


class GroupAuthSerializer(serializers.ModelSerializer, BaseModelSerializer):

    class Meta:
        model = GroupAuth
        exclude = ('deleted', )


class ReturnGroupSerializer(serializers.ModelSerializer, BaseModelSerializer):
    back_auths = GroupAuthSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        exclude = ('deleted',) 


class UserInfoSerializer(serializers.ModelSerializer, BaseModelSerializer):
    group = ReturnGroupSerializer()
    bf_logo_time = serializers.DateTimeField(label='上次登录时间', format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = User
        exclude = ('deleted', 'password',)


# 登录view的表单验证
class LoginViewSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class AddUserSerializer(serializers.ModelSerializer, BaseModelSerializer):

    class Meta:
        model = User
        exclude = ('deleted',)


class UserUseGroupSerializer(serializers.ModelSerializer, BaseModelSerializer):

    class Meta:
        model = Group
        exclude = ('deleted',) 


class ReturnUserSerializer(serializers.ModelSerializer, BaseModelSerializer):
    group = UserUseGroupSerializer()
    bf_logo_time = serializers.DateTimeField(label='上次登录时间', format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = User
        exclude = ('deleted', 'password',)


class AddGroupSerializer(serializers.ModelSerializer, BaseModelSerializer):
    group_type = serializers.CharField(label="用户组类型", help_text="用户组类型", required=True, allow_blank=False,
                                       validators=[UniqueValidator(queryset=Group.all_objects.all(), message="用户组类型已经存在")])

    class Meta:
        model = Group
        exclude = ('deleted',) 