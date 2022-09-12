from django.db import models
from extensions.BaseModel import BaseModel


class User(BaseModel):
    # 管理员时使用账户密码登录
    gender_choice = (
        ('privacy', '保密'), 
        ('male', '男'), 
        ('female', '女')
    )
    username = models.CharField(max_length=32, default='', blank=True, verbose_name='用户账号')
    password = models.CharField(max_length=255, default='',blank=True, verbose_name='用户密码')
    mobile = models.CharField(max_length=16, default='', blank=True, verbose_name='手机号')
    email = models.EmailField(default='', blank=True, verbose_name='邮箱')
    nick_name = models.CharField(max_length=32, default='', blank=True, verbose_name='昵称')
    region = models.CharField(max_length=255, default='', blank=True, verbose_name='地区')
    avatar_url = models.CharField(max_length=255, default='', blank=True, verbose_name='头像')
    gender = models.CharField(max_length=64, choices=gender_choice, default='privacy', verbose_name='性别')
    birth_date = models.CharField(max_length=10, default='', blank=True, verbose_name='生日')
    is_freeze = models.BooleanField(default=False, verbose_name='是否冻结/是否封号')
    bf_logo_time = models.BigIntegerField(default=0, verbose_name='上次登录时间戳')
    jwt_version = models.IntegerField(default=0, verbose_name='jwt token版本')
    # is_admin = models.BooleanField(default=False, verbose_name='是否管理员')
    # group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='用户组')
    # 组权分离后 当有权限时必定为管理员类型用户，否则为普通用户
    # auth = models.ForeignKey(Auth, on_delete=models.PROTECT, null=True, blank=True, verbose_name='权限组') # 当auth被删除时，当前user的auth会被保留，但是auth下的auth_permissions会被删除，不返回
    

    class Meta:
        db_table = 'a_user_table'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name