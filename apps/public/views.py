import os
import sys
import json
import time
import logging
import threading
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.conf import settings
from django.db import transaction
from django.core.cache import caches
from django.forms.models import model_to_dict
from django.http.response import HttpResponseNotFound
from django.db.models import F, Q, Count, Sum, Max, Min
from django.contrib.auth.hashers import check_password, make_password
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from extensions.JwtToken import JwtToken
from extensions.Pagination import Pagination
from extensions.Throttle import VisitThrottle
from extensions.MyResponse import MyJsonResponse
from extensions.JwtAuth import JwtAuthentication
from extensions.Permission import IsAuthPermission
from PIL import Image
from .models import *
from .serializers import *
from .tasks import *
# from .filters import *
# 不建议导入所有，建议按需导入


class UploadLocalFile(APIView):
    authentication_classes = (JwtAuthentication, )
    permission_classes = (IsAuthPermission, )
    throttle_classes = (VisitThrottle, )
    
    def post(self, request):
        '''
        上传接口-写入本地
        '''
        res = MyJsonResponse()
        try:
            file_i = request.FILES.items()
            key_name, up_file = next(file_i)
            logging.debug("%s %s %s" % (key_name, up_file.name, up_file.size))
            file_name = up_file.name
            file_size = up_file.size
            check_file = os.path.splitext(file_name)[1]
            if check_file[1:].lower() not in settings.IMAGE_FILE_CHECK:
                res.update(message='{} Not the specified type, allow type({})! '.format(file_name, '/'.join(settings.IMAGE_FILE_CHECK)), errorCode=2)
                return res.data
            if file_size > settings.IMAGE_FILE_SIZE:
                res.update(message="{} file more than {} mb, Can't upload! ".format(file_name, settings.IMAGE_FILE_SIZE / 1024 / 1024), errorCode=2)
                return res.data
            # 创建当月的目录
            base_dir = os.path.join(settings.UPLOAD_DIR, datetime.datetime.now().strftime('%Y-%m-%d'))
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
                os.chmod(base_dir, mode=0o755)
            # 得到目录+文件名
            file_name = os.path.join(datetime.datetime.now().strftime('%Y-%m-%d'), '%su' % request.user.id + str(uuid4()).replace('-', '') + check_file.lower())
            # 实际保存的路径
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            if check_file[1:].lower() in ('jpg', 'jpeg'):
                im = Image.open(up_file)
                im.save(file_path, quality=75)
            else:
                with open(file_path, 'wb') as u_file:
                    for part in up_file.chunks():
                        u_file.write(part)
            host_file_url = settings.SERVER_NAME + '/files/' + file_name
            res.update(data={key_name: host_file_url})
            os.chmod(file_path, mode=0o644)
            return res.data
        except StopIteration:
            res.update(message="File not uploaded", errorCode=2)
            return res.data
        except Exception as e:
            logging.error('happen error: %s' % e)
            logging.exception(e)
            res.update(message="An unexpected view error occurred: {}".format(e), errorCode=1)
            return res.data