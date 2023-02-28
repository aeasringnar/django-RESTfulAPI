from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector
from rest_framework.pagination import CursorPagination, LimitOffsetPagination, PageNumberPagination


class MyDjangoRestResponsePagination(PaginatorInspector):
    """自定义分页返回的schema"""

    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        if isinstance(paginator, (LimitOffsetPagination, PageNumberPagination, CursorPagination)):
            has_count = not isinstance(paginator, CursorPagination)
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('total', openapi.Schema(type=openapi.TYPE_INTEGER) if has_count else None),
                    ('msg', openapi.Schema(type=openapi.TYPE_STRING)),
                    ('code', openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ('next', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('previous', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('data', response_schema),
                )),
                required=['data']
            )

            if has_count:
                paged_schema.required.insert(0, 'total')

        return paged_schema
