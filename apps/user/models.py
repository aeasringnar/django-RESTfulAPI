from django.db import models
from soft_delete_it.models import SoftDeleteModel
from base.models import BaseModel


class Group(SoftDeleteModel, BaseModel):
    group_type_choices = (
        ('SuperAdmin', '超级管理员'),
        ('Admin', '管理员'),
        ('NormalUser', '普通用户'),
    )
    group_type = models.CharField(max_length=255, choices=group_type_choices, verbose_name='用户组类型')
    group_type_cn = models.CharField(max_length=255, verbose_name='用户组类型-cn')

    class Meta:
        db_table = 'A_Group_Table'
        verbose_name = '用户组表'
        verbose_name_plural = verbose_name


class Auth(SoftDeleteModel, BaseModel):
    auth_type = models.CharField(max_length=255, verbose_name='权限名称')

    class Meta:
        db_table = 'A_Auth_Table'
        verbose_name = '权限组表'
        verbose_name_plural = verbose_name


class AuthPermission(SoftDeleteModel, BaseModel):
    object_name = models.CharField( max_length=255, verbose_name='功能名称')
    object_name_cn = models.CharField(max_length=255, verbose_name='功能名称-中文')
    auth = models.ForeignKey(Auth, on_delete=models.PROTECT, verbose_name='权限组', related_name='auth_permissions')
    auth_list = models.NullBooleanField(default=False, verbose_name='查看')
    auth_create = models.NullBooleanField(default=False, verbose_name='新增')
    auth_update = models.NullBooleanField(default=False, verbose_name='修改')
    auth_destroy = models.NullBooleanField(default=False, verbose_name='删除')

    class Meta:
        db_table = 'A_AuthPermission_Table'
        verbose_name = '权限菜单表'
        verbose_name_plural = verbose_name


class User(SoftDeleteModel, BaseModel):
    status_type_choices = (
        (0, '冻结'),
        (1, '正常'),
    )
    username = models.CharField(max_length=255, verbose_name='用户账号')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='用户手机号')
    email = models.EmailField(null=True, blank=True, verbose_name='用户邮箱')
    password = models.CharField(max_length=255, default='123456', verbose_name='用户密码')
    real_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='姓名or昵称')
    region = models.CharField(max_length=255, null=True, blank=True, verbose_name='地区')
    avatar_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='头像')
    open_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='微信openid')    
    gender = models.IntegerField(choices=((0, '未知'), (1, '男'), (2, '女')), default=0, verbose_name='性别')
    birth_date = models.DateField(verbose_name='生日', null=True, blank=True)
    status = models.IntegerField(default=1, choices=status_type_choices,  verbose_name='用户状态')
    is_admin = models.BooleanField(default=False, verbose_name='是否管理员')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='用户组')
    auth = models.ForeignKey(Auth, on_delete=models.PROTECT, null=True, blank=True, verbose_name='权限组')
    bf_logo_time = models.DateTimeField(null=True, blank=True, verbose_name='上次登录时间')

    class Meta:
        db_table = 'A_User_Table'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name