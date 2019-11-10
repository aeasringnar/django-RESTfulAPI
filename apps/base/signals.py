from datetime import datetime
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ConfDict
from django.db import transaction


@transaction.atomic
@receiver(post_save, sender=ConfDict)
def create_update_object(sender, instance=None, created=False, **kwargs):
    '''
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    '''
    print('对象保存时 signals流转详情：')
    print(sender)
    if created:
        print('新增时：', instance)
    else:
        print('修改时：', instance)
    

@transaction.atomic
@receiver(post_delete, sender=ConfDict)
def delete_object(sender, instance=None, **kwargs):
    '''
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    '''
    print('对象删除时 查看signals流转详情：')
    print(sender)
    print('被删除的对象：', instance)