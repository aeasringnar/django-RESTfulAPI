from drf_yasg.generators import OpenAPISchemaGenerator
from django.urls import get_resolver, URLPattern, URLResolver


def get_all_url(resolver=None, pre='/'):
    if resolver is None:
        resolver = get_resolver()
    for r in resolver.url_patterns:
        if isinstance(r, URLPattern):
            if '<pk>' in str(r.pattern):
                continue
            yield pre + str(r.pattern).replace('^', '').replace('$', ''), r.name
        if isinstance(r, URLResolver):
            yield from get_all_url(r, pre + str(r.pattern))

class BaseOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    '''重写 OpenAPISchemaGenerator 手动为每个路由添加 tag'''

    def get_schema(self, request=None, public=False):
        '''重写父类方法'''
        swagger = super().get_schema(request, public)
        swagger.tags = [
            {
                'name': 'AdminLogin',
                'description': '管理用户接口'
            },
            {
                'name': 'Logout',
                'description': '退出登录接口'
            },
        ]
        return swagger