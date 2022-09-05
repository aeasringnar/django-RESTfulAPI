import time
from typing import *
from datetime import datetime
from django.db.models import Model, Manager
from django.db import models


class BigDataFilterManager(Manager):
    
    def all(self, filter_time=None):
        if filter_time:
            if ',' in filter_time:
                start_time = datetime.datetime.strptime(filter_time.split(',')[0] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                end_time = datetime.datetime.strptime(filter_time.split(',')[1] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                return super().all().filter(create_time__gte=start_time, create_time__lte=end_time)
            return super().all()
        return super().all()


class BaseModel(Model):
    # sort = models.IntegerField(default=1, verbose_name='排序')
    remark = models.TextField(max_length=1024, default='', blank=True, verbose_name='备注')
    sort_timestamp = models.BigIntegerField(verbose_name='排序时间戳，默认等于创建时间戳')
    create_timestamp = models.BigIntegerField(verbose_name='创建时间戳')
    update_timestamp = models.BigIntegerField(verbose_name='更新时间戳')
    # objects = BigDataFilterManager()  # 是否开放大数据时的日期过滤

    class Meta:
        abstract = True
    
    def save(self, force_insert: bool, force_update: bool, using: Optional[str], update_fields: Optional[Iterable[str]]) -> None:
        now_time = int(time.time() * 1000)
        print("数据正则创建")
        print(dir(self))
        self.update_time = now_time
        return super().save(force_insert, force_update, using, update_fields)
    
    def delete(self, using: Any, keep_parents: bool) -> Tuple[int, Dict[str, int]]:
        now_time = int(time.time() * 1000)
        print("数据正则删除")
        print(dir(self))
        self.update_time = now_time
        return super().delete(using, keep_parents)