from comment.myapps.my_softdelete_models import SafeModel
from django.db import models
from public.models import BaseModel


class Banner(SafeModel, BaseModel):
    '''
    轮播图
    '''
    jump_type_choices = (
        (0, '外链'),
        (1, '内链')
    )
    title = models.CharField(max_length=255, verbose_name='标题')
    img_url = models.CharField(max_length=255, verbose_name='图片链接')
    jump_type = models.IntegerField(choices=jump_type_choices, default=0, verbose_name='跳转分类')
    jump_url = models.CharField(max_length=255, default='', verbose_name='外链链接')
    start_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)

    class Meta:
        db_table = 'A_Banner_table'
        verbose_name = '轮播图表'
        verbose_name_plural = verbose_name