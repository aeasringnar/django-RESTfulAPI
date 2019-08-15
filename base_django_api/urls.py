from base.views import UploadFile, Tests
from user.views import LoginView, UserViewset, UserInfo, GroupViewset
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 新版swagger
from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Django RESTfulAPI",
        default_version='v2',
        description="Ddescription",
        terms_of_service="https://blog.csdn.net/haeasringnar",
        contact=openapi.Contact(email="aeasringnar@163.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
# 使用 viewset 路由管理
router = DefaultRouter()
# 账号管理
router.register(r'user', UserViewset, base_name='账号管理')
# 角色管理
router.register(r'groups', GroupViewset, base_name='角色管理')
from tests.views import FtableViewset, StableViewset, BeginCelery
# 测试父表管理
router.register(r'ftable', FtableViewset, base_name='测试父表管理')
# 测试子表管理
router.register(r'stable', StableViewset, base_name='测试子表管理')


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
    path('adminlogin/', LoginView.as_view(), name='adminlogin'),
    path('uploadfile/', UploadFile.as_view(), name='uploadfile'),
    path('tests/', Tests.as_view(), name='tests'),
    path('userinfo/', UserInfo.as_view(), name='userinfo'),
    path('celery/', BeginCelery.as_view(), name='tests'),
]
