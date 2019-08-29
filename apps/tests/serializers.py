
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

# 新增权限菜单使用
class AddAdminMenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdminMenu
        fields = ['id','base_name', 'base_name_cn','menu_list','menu_create','menu_update','menu_destroy']

# 新增 权限组表 序列化器
class AddUserPermissionsSerializer(serializers.ModelSerializer, BaseSerializer):
    permission_type = serializers.CharField(label="权限名称", help_text="权限名称", required=True, allow_blank=False,
                                       validators=[UniqueValidator(queryset=UserPermissions.objects.all(), message="该权限已经存在")])
    admin_menu = AddAdminMenuSerializer(many=True)
    class Meta:
        model = UserPermissions
        fields = '__all__' 
    def create(self, validated_data):
        auth_permissions_data = validated_data.pop('admin_menu')
        user_permission = UserPermissions.objects.create(**validated_data)
        # 创建权限菜单的方法
        for item in auth_permissions_data:
            AdminMenu.objects.create(user_permission=user_permission, **item)
        return user_permission

    def update(self, instance, validated_data):
        print('查看admin_menu：', validated_data.get('admin_menu'))
        if validated_data.get('admin_menu'):
            auth_permissions_data = validated_data.pop('admin_menu')
            # 创建权限菜单的方法
            need_dels = AdminMenu.objects.filter(user_permission_id=instance.id)
            for item in need_dels:
                item.delete()
            for item in auth_permissions_data:
                print('查看：', item)
                print('查看id：', item.get('id'))
                AdminMenu.objects.create(user_permission=instance, **item)
        
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
                


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
                