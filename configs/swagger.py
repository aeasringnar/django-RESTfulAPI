from drf_yasg.generators import OpenAPISchemaGenerator
from django.urls import get_resolver, URLPattern, URLResolver


def get_all_url(resolver=None, pre='/'):
    if resolver is None:
        resolver = get_resolver()
    for r in resolver.url_patterns:
        if isinstance(r, URLPattern):
            if '<pk>' in str(r.pattern) or r.name == 'api-root' or '\\.(?P<format>[a-z0-9]+)/?' in str(r.pattern):
                continue
            yield pre + str(r.pattern).replace('^', '').replace('$', ''), r.name
        if isinstance(r, URLResolver):
            yield from get_all_url(r, pre + str(r.pattern))