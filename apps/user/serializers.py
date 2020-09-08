from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from public.serializers import BaseModelSerializer
from rest_framework.utils import model_meta
from .models import *
import time
import datetime
import threading
from django.db import transaction


# 新增权限菜单约束使用
class AddAuthPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthPermission
        fields = ['id','object_name', 'object_name_cn','auth_list','auth_create','auth_update','auth_destroy']


def del_worker(datas):
    for item in datas:
        item.delete()


def save_worker(instance, datas):
    for item in datas:
        AuthPermission.objects.create(auth=instance, **item)


# 新增权限使用
class AddAuthSerializer(serializers.ModelSerializer):
    auth_permissions = AddAuthPermissionSerializer(many=True)

    class Meta:
        model = Auth
        exclude = ('deleted',)
        validators = [UniqueTogetherValidator(queryset=Auth.objects.all(), fields=['auth_type',], message='该权限已经存在')]

    @transaction.atomic
    def create(self, validated_data):
        auth_permissions_data = validated_data.pop('auth_permissions')
        auth_per = Auth.objects.create(**validated_data)
        # 创建权限菜单的方法
        for item in auth_permissions_data:
            AuthPermission.objects.create(auth=auth_per, **item)
        return auth_per

    @transaction.atomic
    def update(self, instance, validated_data):
        # print('查看auth_permissions：', validated_data.get('auth_permissions'))
        if validated_data.get('auth_permissions'):
            auth_permissions_data = validated_data.pop('auth_permissions')
            # 修改时创建权限菜单的方法
            need_dels = AuthPermission.objects.filter(auth_id=instance.id)
            for item in need_dels:
                item.delete()
            for item in auth_permissions_data:
                # print('查看：', item)
                # print('查看id：', item.get('id'))
                AuthPermission.objects.create(auth=instance, **item)
            # 开多线程优化代码
            # del_work = threading.Thread(target=del_worker,args=(need_dels,))
            # del_work.start()
            # save_work = threading.Thread(target=save_worker,args=(instance,auth_permissions_data,))
            # save_work.start()
            # save_work.join()

        # 继承自父类的方法
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


# 返回权限使用
class ReturnAuthSerializer(serializers.ModelSerializer):
    auth_permissions = AddAuthPermissionSerializer(read_only=True, many=True)

    class Meta:
        model = Auth
        exclude = ('deleted',)


# 后台登录view的表单验证
class LoginViewSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    # test = serializers.DictField(child=serializers.CharField(required=True))


# 新增后台用户使用
class AddUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('deleted',)
        validators = [
            UniqueTogetherValidator(queryset=User.objects.all(), fields=['mobile',], message='该手机号已经存在'),
            UniqueTogetherValidator(queryset=User.objects.all(), fields=['email',], message='该邮箱已经存在'),
            UniqueTogetherValidator(queryset=User.objects.all(), fields=['username',], message='该登录名已经存在')
            ]

    def validate(self, attrs):
        now_user = self.context['request'].user
        print(attrs['group'].group_type)
        if attrs['group'].group_type == 'SuperAdmin' and now_user.group.group_type != 'SuperAdmin':
            raise serializers.ValidationError("无权建立超级管理员账号。")
        if attrs['group'].group_type == 'NormalUser' and now_user.group.group_type != 'SuperAdmin':
            raise serializers.ValidationError("无权私自建立普通用户账号。")
        return attrs

# 修改后台用户使用
class UpdateUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('deleted',)
        validators = [
            UniqueTogetherValidator(queryset=User.objects.all(), fields=['mobile',], message='该手机号已经存在'),
            UniqueTogetherValidator(queryset=User.objects.all(), fields=['username',], message='该登录名已经存在')
            ]

    def validate(self, attrs):
        now_user = self.context['request'].user
        if attrs.get('group') and now_user.group.group_type != 'SuperAdmin':
            raise serializers.ValidationError("无权修改用户组。")
        return attrs


# ReturnUserSerializer 使用的group序列化器
class UserUseGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        exclude = ('deleted',) 


# 返回用户使用 userinfo也使用
class ReturnUserSerializer(serializers.ModelSerializer):
    group = UserUseGroupSerializer()
    auth = ReturnAuthSerializer()

    class Meta:
        model = User
        exclude = ('deleted', 'password',)


# 微信MINI登录view的表单验证
class WeChatLoginViewSerializer(serializers.Serializer):
    code = serializers.CharField()
    userInfo = serializers.JSONField()
    iv = serializers.CharField()
    encrypted_data = serializers.CharField()


# 微信APP登录view的表单验证
class WeChatAppLoginViewSerializer(serializers.Serializer):
    code = serializers.CharField()


# 用户修改个人信息序列化器
class WeChatUpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['mobile', 'email', 'region', 'real_name', 'id_num', 'nick_name', 'gender', 'avatar_url', 'birth_date'] 


# 后台修改普通用户序列化器
class UpdateMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['is_freeze']


# 后台返回普通用户序列化器
class ReturnMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('deleted', 'password', 'group', 'auth')


# 发生短信form
class MobileFormSerializer(serializers.Serializer):
    mobile = serializers.CharField()


# 手机号快捷登录form
class MobileLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    code = serializers.CharField()