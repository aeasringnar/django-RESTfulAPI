from public.views import UploadFile, TestView, BeginCelery, ConfDictViewset, UploadLocalFile, test_fuc
from user.views import LoginView, UserViewset, UserInfo, AuthViewset, WeChatUpdateUserViewset, WeChatMiniLoginView, WeChatAppLoginView, MemberViewset, MobileLoginView, MobileCodeView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
# 新版swagger
from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Django RESTfulAPI",
        default_version='v3.0',
        description="Ddescription",
        terms_of_service="https://blog.csdn.net/haeasringnar",
        contact=openapi.Contact(email="aeasringnar@163.com"),
        license=openapi.License(name="MIT License"),
    ),
    url="http://www.test.com",
    public=True,
    permission_classes=(permissions.AllowAny,),
)
# 使用 viewset 路由管理
router = DefaultRouter()
# 账号管理
router.register(r'user', UserViewset, basename='账号管理')
# 普通用户管理
router.register(r'member', MemberViewset, basename='用户管理')
# 权限管理
router.register(r'auth', AuthViewset, basename='权限管理')
# 系统字典管理
router.register(r'confdict', ConfDictViewset, basename='系统字典管理')
# 全文检索路由 检索系统字典
# router.register(r'searchdict', ConfDictSearchView, basename='全文检索系统字典')
# 修改用户个人信息
router.register(r'updateuser', WeChatUpdateUserViewset, basename='修改个人信息')


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
    path('adminlogin/', LoginView.as_view(), name='后台登录'),
    path('wxminilogin/', WeChatMiniLoginView.as_view(), name='微信小程序登录'),
    path('wxapplogin/', WeChatAppLoginView.as_view(), name='微信APP三方登录'),
    path('mobilelogin/', MobileLoginView.as_view(), name='手机快速登录登录'),
    path('getcode/', MobileCodeView.as_view(), name='获取手机验证码'),
    path('uploadfile/', UploadLocalFile.as_view(), name='文件上传'), # UploadFile UploadLocalFile 
    path('test/', TestView.as_view(), name='测试接口'),
    path('userinfo/', UserInfo.as_view(), name='个人信息'),
    path('celery/', BeginCelery.as_view(), name='celery测试'),
    path('test_fuc/', test_fuc, name='celery测试'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path(r'__debug__/', include(debug_toolbar.urls)))
