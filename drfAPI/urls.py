"""drfAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from extensions.MyCache import CacheVersionControl
from configs.swagger import get_all_url
from django.conf import settings


schema_view = get_schema_view(
    openapi.Info(
        title="Django RESTfulAPI",
        default_version='v3.0',
        description="Ddescription",
        terms_of_service="https://blog.csdn.net/haeasringnar",
        contact=openapi.Contact(email="aeasringnar@163.com"),
        license=openapi.License(name="MIT License"),
    ),
   public=True,
   permission_classes=[AllowAny],
)

urlpatterns = [
    path('user/', include(("apps.user.urls", '用户管理')), name="用户管理"),
    path('public/', include(("apps.public.urls", '公共接口')), name="公共接口")
]

# 初始化缓存版本号
all_paths = [item[0] for item in get_all_url()]
CacheVersionControl(all_paths).init_data()

if settings.CURRENT_ENV == "dev":
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]