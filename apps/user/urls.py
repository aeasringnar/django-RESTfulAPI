from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestView, UserViewSet, OwnerUserInfoViewset, AdminLoginView


router = DefaultRouter()
router.register(r'user', UserViewSet, basename="用户管理")
router.register(r'ownerUserInfo', OwnerUserInfoViewset, basename="获取自己的用户信息")
urlpatterns = [
    path('', include(router.urls)),
    path('adminLogin/', AdminLoginView.as_view(), name='后台登录接口'),
    path('test/', TestView.as_view(), name='测试接口'),
]
