import re
from django.db.models import Q
from rest_framework import serializers, status, generics
# 使用APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime,time,random
# 缓存配置
from django.core.cache import cache
# JWT配置
from .utils import jwt_payload_handler, jwt_encode_handler,google_otp
from .authentication import JWTAuthentication
from .models import *
from .serializers import *
import uuid,os,requests, json


# 登录的view
class LoginInfoSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class Login(generics.GenericAPIView):
    serializer_class = LoginInfoSerializer
    def post(self,request):
        # print(request.data)
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            data = (serializer.data)
            username = data.get('username')
            password = data.get('password')
            if username.find('@') == -1 or username.find('.') == -1:
                phone = username
                email = None
            else:
                email = username
                phone = None
            phone_re = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|7[0135678]|8[0-9])\d{8}$', re.IGNORECASE)
            email_re = re.compile(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', re.IGNORECASE)
            user = object
            if phone:
                if not phone_re.match(phone):
                    return Response({"message": "手机号格式错误>_<", "errorCode": 2, "data": {}})
                user = User.objects.filter(is_delete=False,phone=phone).first()
                if not user:
                    return Response({"message": "用户不存在>_<", "errorCode": 2, "data": {}})
            if email:
                if not email_re.match(email):
                    return Response({"message": "邮箱格式错误>_<", "errorCode": 2, "data": {}})
                user = User.objects.filter(is_delete=False,email=email).first()
                if not user:
                    return Response({"message": "用户不存在>_<", "errorCode": 2, "data": {}})
            if user.password == password:
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                return Response({"message": "登录成功>_<", "errorCode": 0, "data": {'token':token}})
            else:
                return Response({"message": "密码错误>_<", "errorCode": 0, "data": {}})
        except Exception as e:
            print(e)
            return Response({"message": "未知错误>_<", "errorCode": 1, "data": {}})
