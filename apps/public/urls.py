from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from .views import UploadLocalFileView, TestView, GetAllEnumDataView


router = DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
    path('uploadFile/', UploadLocalFileView.as_view(), name='上传文件到本地接口'),
    path('test/', TestView.as_view(), name='测试接口'),
]

if settings.CURRENT_ENV == 'dev':
    urlpatterns.extend([
        path('getAllEnumData/', GetAllEnumDataView.as_view(), name='获取内部所有枚举类型数据'),
    ])