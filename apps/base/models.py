from django.db import models
from soft_delete_it.models import SoftDeleteModel
'''
objects 返回没有删除的所有数据
all_objects 返回所有数据
delete 删除数据，假删
undelete 恢复假删数据
'''

class BaseModel(models.Model):
    sort = models.IntegerField(default=1, null=True, blank=True, verbose_name='排序')
    content = models.TextField(default='', null=True, blank=True, verbose_name='描述')
    sort_time = models.DateTimeField(auto_now_add=True, verbose_name='排序时间')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class ConfDict(SoftDeleteModel, BaseModel):
    dict_type_choices = (
        ('0', '类型一'),
        ('1', '类型二'),
        ('2', '类型三'),
    )
    dict_title = models.CharField(max_length=255, verbose_name='字典标题')
    dict_key = models.IntegerField(default=0, verbose_name='字典键值')
    dict_type = models.CharField(max_length=255, default='0', choices=dict_type_choices, verbose_name='字典类型')

    class Meta:
        db_table = 'A_ConfDict_Table'
        verbose_name = '系统字典表'
        verbose_name_plural = verbose_name


class TmpFile(SoftDeleteModel, BaseModel):
    name = models.CharField(default='', null=True, max_length=255)
    url = models.FileField(upload_to="base-api/%Y%m")

    class Meta:
        db_table = 'A_Tmp_File'
        verbose_name = '文件转存表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name