from django_filters import rest_framework as filters
from django.db.models import Q
from django.db.models import F
import datetime
from .models import *


# class MyFilter(filters.FilterSet):
#     '''
#     过滤类
#     '''
#     my_type = filters.CharFilter(field_name='my_type', method='return_my_type', label='自定义类型过滤')
#     filter_date = filters.CharFilter(field_name='filter_date', method='return_filter_date', label='时间段过滤')

#     class Meta:
#         model = NewModels
#         fields = ['status', ]

#     def return_my_type(self, queryset, name, value):
#         print('查看传递的值：', value)
#         if value == '0':
#             return queryset.filter(Q(my_type=0) | Q(my_type=2) | Q(my_type=4))
#         elif value == '1':
#             return queryset.filter(Q(my_type=1) | Q(my_type=3) | Q(my_type=5))
#         else:
#             return queryset.all()
    
#     def return_filter_date(self, queryset, name, value):
#         print('查看传递的值：', value)
#         if ',' not in value:
#             return queryset.all()
#         else:
#             date_list = value.split(',')
#             start_date = datetime.datetime.strptime(date_list[0], '%Y-%m-%d')
#             end_date = datetime.datetime.strptime(date_list[1] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
#             return queryset.filter(updated__gt=start_date, updated__lt=end_date)

