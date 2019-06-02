from django.db import models
from soft_delete_it.models import SoftDeleteModel
from base.models import BaseModel

class Group(SoftDeleteModel, BaseModel):
    group_type = models.CharField(max_length=255, verbose_name='用户组类型')

    class Meta:
        db_table = 'A_Group_Table'
        verbose_name = '用户组表'
        verbose_name_plural = verbose_name


class GroupAuth(SoftDeleteModel, BaseModel):
    object_name = models.CharField( max_length=255, default='', verbose_name='功能名称')
    object_name_cn = models.CharField(max_length=255, default='', verbose_name='功能名称-中文')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='所属用户组', related_name='back_auths')
    auth_list = models.NullBooleanField(default=False, verbose_name='查看')
    auth_create = models.NullBooleanField(default=False, verbose_name='新增')
    auth_update = models.NullBooleanField(default=False, verbose_name='修改')
    auth_destroy = models.NullBooleanField(default=False, verbose_name='删除')

    class Meta:
        db_table = 'A_GroupAuth_Table'
        verbose_name = '后台用户组菜单表'
        verbose_name_plural = verbose_name


class User(SoftDeleteModel, BaseModel):
    status_type_choices = (
        ('0', '冻结'),
        ('1', '正常'),
    )
    username = models.CharField(max_length=255, verbose_name='用户账号')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='用户手机号')
    email = models.EmailField(default='', null=True, blank=True, verbose_name='用户邮箱')
    password = models.CharField(max_length=255, default='123456', verbose_name='用户密码')
    real_name = models.CharField(max_length=255, default='', null=True, blank=True, verbose_name='姓名')
    status = models.CharField(max_length=255, default='1', choices=status_type_choices,  verbose_name='用户状态')
    is_admin = models.BooleanField(default=False, verbose_name='是否管理员')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='用户组')
    bf_logo_time = models.DateTimeField(null=True, blank=True, verbose_name='上次登录时间')

    class Meta:
        db_table = 'A_User_Table'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name