from django.db import models
from soft_delete_it.models import SoftDeleteModel
'''
objects 返回没有删除的所有数据
all_objects 返回所有数据
delete 删除数据，假删
undelete 恢复假删数据
模型字段类型：
models.CharField() # 字符串类型
models.TextField() # 文本类型
models.IntegerField() # int类型
models.BooleanField() # bool类型
models.NullBooleanField() # 允许为空的bool类型
models.DateField() # 日期类型 年月日
models.DecimalField() # 金额类型 可以指定长度和小数位数 max_digits=15, decimal_places=2, 总长度15位，小数位为2
models.EmailField() # 邮箱类型
models.FloatField() # 浮点数类型
models.TimeField() # 时间类型
models.ForeignKey(OtherModel, on_delete=models.PROTECT, verbose_name='label', related_name='related_name') # 外键类型
models.OneToOneField(OtherModel, on_delete=models.PROTECT, verbose_name='label', related_name='related_name') # 一对一的外键类型
模型常用options：
null = True # 允许值为空
blank = True # 允许键为空，指定的字段可以不传
choices = ((0,'男'),('1','女'),) # 选项类型
default = 1 # 指定默认值
verbose_name = '描述' # 指定label 或字段描述
auto_now_add = True # 在创建的时候插入时间
auto_now = True # 每次修改都会更新时间
max_length = 255 # 指定字段容量长度，CharField必须要指定
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