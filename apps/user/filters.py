import time
import logging
from datetime import datetime
from django_filters.rest_framework import FilterSet, CharFilter
from django.db.models import Q, F
from django.db import transaction


# class MyFilter(FilterSet):
#     '''
#     过滤类
#     '''
#     my_type = CharFilter(field_name='my_type', method='return_my_type', label='自定义类型过滤')
#     filter_date = CharFilter(field_name='filter_date', method='return_filter_date', label='时间段过滤')

#     class Meta:
#         model = YourModels
#         fields = ['status', ] # 原本支持的过滤字段

#     def return_my_type(self, queryset, name, value):
#         logging.debug(f'查看传递的值：{value}')
#         if value == '0':
#             return queryset.filter(Q(my_type=0) | Q(my_type=2) | Q(my_type=4))
#         elif value == '1':
#             return queryset.filter(Q(my_type=1) | Q(my_type=3) | Q(my_type=5))
#         else:
#             return queryset.all()
    
#     def return_filter_date(self, queryset, name, value):
#         logging.debug(f'查看传递的值：{value}')
#         if ',' not in value:
#             return queryset.all()
#         else:
#             date_list = value.split(',')
#             start_date = datetime.strptime(date_list[0], '%Y-%m-%d')
#             end_date = datetime.strptime(date_list[1] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
#             return queryset.filter(update_time__gt=start_date, update_time__lt=end_date)