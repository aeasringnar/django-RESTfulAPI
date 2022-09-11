# from typing import *
from datetime import datetime
from django.db.models import Model, Manager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from utils.MyDateTime import MyDateTime
from extensions.MyFields import TimestampField


class BigDataFilterManager(Manager):
    
    def all(self, filter_time=None):
        if filter_time:
            if ',' in filter_time:
                start_time = MyDateTime.datetime_timestamp(datetime.strptime(filter_time.split(',')[0] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
                end_time = MyDateTime.datetime_timestamp(datetime.strptime(filter_time.split(',')[1] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
                return super().all().filter(create_timestamp__gte=start_time, update_timestamp__lte=end_time)
            return super().all()
        return super().all()


class BaseModel(Model):
    # sort = models.IntegerField(default=1, verbose_name='排序')
    remark = models.TextField(max_length=1024, default='', blank=True, verbose_name='备注')
    sort_timestamp = TimestampField(auto_now_add=True, validators=[MinValueValidator(limit_value=0)], verbose_name='排序时间戳，默认等于创建时间戳')
    create_timestamp = TimestampField(auto_now_add=True, validators=[MinValueValidator(limit_value=0)], verbose_name='创建时间戳')
    update_timestamp = TimestampField(auto_now=True,validators=[MinValueValidator(limit_value=0)], verbose_name='更新时间戳')
    # objects = BigDataFilterManager()  # 是否开放大数据时的日期过滤

    class Meta:
        abstract = True
    
    # 已废弃。废弃原因：在批量创建和删除时无法覆盖到save和delete，现在的方案是利用自定义字段和自定义manager queryset
    # @transaction.atomic
    # def save(self, *args, **kwargs) -> None:
    #     now_time = int(time.time() * 1e6)
    #     # print(dir(self))
    #     if self.pk is None:
    #         # print("数据正则创建")
    #         self.create_timestamp = now_time
    #         self.sort_timestamp = now_time
    #     else:
    #         pass
    #         # print("数据正则修改")
    #     self.update_timestamp = now_time
    #     super().save(*args, **kwargs)
    
    @transaction.atomic
    def delete(self, *args, **kwargs) -> None:
        self.update_timestamp = MyDateTime.datetime_timestamp(datetime.now())
        super().delete(*args, **kwargs)