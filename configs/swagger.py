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
                'name': 'user',
                'description': '用户管理接口'
            },
            {
                'name': 'public',
                'description': '公共接口'
            },
        ]
        return swagger


from drf_yasg.inspectors import SwaggerAutoSchema

class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        tags = super().get_tags(operation_keys)
        print('-' * 128)
        print(tags)
        print(operation_keys)
        if "v1" in tags and operation_keys:
            #  `operation_keys` 内容像这样 ['v1', 'prize_join_log', 'create']
            tags[0] = operation_keys[1]

        return tags