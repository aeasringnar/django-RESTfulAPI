from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from extensions.BaseModel import BaseModel


class ConfDict(BaseModel):
    dict_type_choices = (
        ('ip_white', 'IP白名单'),
        ('ip_black', 'IP黑名单'),
    )
    dict_key = models.CharField(max_length=255, verbose_name='字典键')
    dict_value = models.CharField(max_length=255, verbose_name='字典值')
    dict_type = models.CharField(max_length=255, default='', choices=dict_type_choices, verbose_name='字典类型')

    class Meta:
        db_table = 'api_conf_dict'
        verbose_name = '系统字典表'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['dict_key']),
        ]
        unique_together = [
            ['dict_key', 'deleted'],
        ]