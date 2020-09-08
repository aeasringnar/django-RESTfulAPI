from django.db import models
from soft_delete_new.models import SoftDeleteModel
from public.models import BaseModel


class Group(SoftDeleteModel, BaseModel):
    group_type_choices = (
        ('SuperAdmin', '超级管理员'),
        ('Admin', '管理员'),
        ('NormalUser', '普通用户'),
    )
    group_type = models.CharField(max_length=128, choices=group_type_choices, verbose_name='用户组类型')
    group_type_cn = models.CharField(max_length=128, verbose_name='用户组类型_cn')

    class Meta:
        db_table = 'A_Group_Table'
        verbose_name = '用户组表'
        verbose_name_plural = verbose_name


class Auth(SoftDeleteModel, BaseModel):
    auth_type = models.CharField(max_length=128, verbose_name='权限名称')

    class Meta:
        db_table = 'A_Auth_Table'
        verbose_name = '权限组表'
        verbose_name_plural = verbose_name


class AuthPermission(SoftDeleteModel, BaseModel):
    object_name = models.CharField( max_length=128, verbose_name='功能名称')
    object_name_cn = models.CharField(max_length=128, verbose_name='功能名称_cn')
    auth = models.ForeignKey(Auth, on_delete=models.CASCADE, verbose_name='权限组', related_name='auth_permissions')
    auth_list = models.NullBooleanField(default=False, verbose_name='查看')
    auth_create = models.NullBooleanField(default=False, verbose_name='新增')
    auth_update = models.NullBooleanField(default=False, verbose_name='修改')
    auth_destroy = models.NullBooleanField(default=False, verbose_name='删除')

    class Meta:
        db_table = 'A_AuthPermission_Table'
        verbose_name = '权限菜单表'
        verbose_name_plural = verbose_name


class User(SoftDeleteModel, BaseModel):
    # 管理员时使用账户密码登录
    username = models.CharField(max_length=32, default='', blank=True, verbose_name='用户账号')
    password = models.CharField(max_length=255, default='',blank=True, verbose_name='用户密码')
    mobile = models.CharField(max_length=11, default='', blank=True, verbose_name='用户手机号')
    email = models.EmailField(default='', blank=True, verbose_name='用户邮箱')
    real_name = models.CharField(max_length=16, default='', blank=True, verbose_name='真实姓名')
    id_num = models.CharField(max_length=18, default='', blank=True, verbose_name='身份证号')
    nick_name = models.CharField(max_length=32, default='', blank=True, verbose_name='昵称')
    region = models.CharField(max_length=255, default='', blank=True, verbose_name='地区')
    avatar_url = models.CharField(max_length=255, default='', blank=True, verbose_name='头像')
    open_id = models.CharField(max_length=255, default='', blank=True, verbose_name='微信openid') 
    union_id = models.CharField(max_length=255, default='', blank=True, verbose_name='微信unionid')
    gender = models.IntegerField(choices=((0, '未知'), (1, '男'), (2, '女')), default=0, verbose_name='性别')
    birth_date = models.DateField(verbose_name='生日', null=True, blank=True)
    is_freeze = models.IntegerField(default=0, choices=((0, '否'),(1, '是')),  verbose_name='是否冻结/是否封号')
    # is_admin = models.BooleanField(default=False, verbose_name='是否管理员')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='用户组')
    # 组权分离后 当有权限时必定为管理员类型用户，否则为普通用户
    auth = models.ForeignKey(Auth, on_delete=models.PROTECT, null=True, blank=True, verbose_name='权限组') # 当auth被删除时，当前user的auth会被保留，但是auth下的auth_permissions会被删除，不返回
    bf_logo_time = models.DateTimeField(null=True, blank=True, verbose_name='上次登录时间')

    class Meta:
        db_table = 'A_User_Table'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name