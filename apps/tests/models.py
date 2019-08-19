from django.db import models
from soft_delete_it.models import SoftDeleteModel
from base.models import BaseModel

class Ftable(SoftDeleteModel, BaseModel):
    f_type = models.CharField(max_length=255, verbose_name='类型')
    f_key = models.IntegerField(verbose_name='键值')

    class Meta:
        db_table = 'A_Ftable_Table'
        verbose_name = '测试父表'
        verbose_name_plural = verbose_name


class Stable(SoftDeleteModel, BaseModel):
    name = models.CharField( max_length=255, verbose_name='名称')
    desc = models.CharField(max_length=255, verbose_name='描述')
    ftable = models.ForeignKey(Ftable, on_delete=models.PROTECT, verbose_name='父表', related_name='stables')

    class Meta:
        db_table = 'A_Stable_Table'
        verbose_name = '测试子表'
        verbose_name_plural = verbose_name