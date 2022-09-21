from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UploadLocalFileView


router = DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
    path('uploadFile/', UploadLocalFileView.as_view(), name='上传文件到本地接口'),
]