from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.conf import settings


class Pagination(PageNumberPagination):
    # 定pagination类
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100

    def get_my_next(self):
        # print(8888, self.request.path)
        # print(8888, settings.SERVER_NAME)
        # print(8888, self.get_next_link().split(self.request.path))
        return settings.SERVER_NAME + self.request.path + self.get_next_link().split(self.request.path)[1]
    
    def get_my_pre(self):
        return settings.SERVER_NAME + self.request.path + self.get_previous_link().split(self.request.path)[1]

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        })
