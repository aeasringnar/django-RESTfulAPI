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
# from .utils import jwt_payload_handler, jwt_encode_handler,google_otp,request_log
from .utils import *
from .authentication import JWTAuthentication
from .models import *
from .serializers import *
# 内置包
import uuid, os, requests, json, re, time, datetime, random, hashlib, xml
'''
name = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
name = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
name = serializers.FloatField(max_value=None, min_value=None)
name = serializers.IntegerField(max_value=None, min_value=None)
name = serializers.DateTimeField(format=api_settings.DATETIME_FORMAT, input_formats=None)
name = serializers.DateField(format=api_settings.DATE_FORMAT, input_formats=None)
name = serializers.BooleanField()
name = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=100))
'''



# 登录的view
class LoginInfoSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
class Login(generics.GenericAPIView):
    serializer_class = LoginInfoSerializer
    def post(self,request):
        request_log(request)
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
                    return Response({"message": "手机号格式错误", "errorCode": 2, "data": {}})
                user = User.objects.filter(is_delete=False,phone=phone).first()
                if not user:
                    return Response({"message": "用户不存在", "errorCode": 2, "data": {}})
            if email:
                if not email_re.match(email):
                    return Response({"message": "邮箱格式错误", "errorCode": 2, "data": {}})
                user = User.objects.filter(is_delete=False,email=email).first()
                if not user:
                    return Response({"message": "用户不存在", "errorCode": 2, "data": {}})
            if user.password == password:
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                return Response({"message": "登录成功", "errorCode": 0, "data": {'token':token}})
            else:
                return Response({"message": "密码错误", "errorCode": 0, "data": {}})
        except Exception as e:
            print(e)
            return Response({"message": "未知错误", "errorCode": 1, "data": {}})





class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    # captcha = serializers.CharField()
class Register(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    def post(self,request):
        request_log(request)
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            data = (serializer.data)
            username = data.get('username')
            password = data.get('password')
            # captcha = data.get('captcha')
            if username.find('@') == -1 or username.find('.') == -1:
                phone = username
                email = None
            else:
                email = username
                phone = None
            phone_re = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|7[0135678]|8[0-9])\d{8}$', re.IGNORECASE)
            email_re = re.compile(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', re.IGNORECASE)
            if phone:
                if not phone_re.match(phone):
                    return Response({"message": "手机号格式错误", "errorCode": 2, "data": {}})
                account_check = User.objects.filter(phone=phone, is_delete=False)
                if account_check:
                    return Response({"message": "用户已经存在", "errorCode": 2})
                account = User()
                account.phone = phone
                # account.password = create_password(password)
                # 明文密码
                account.password = password
                # account.birthday = datetime.date.today()
                account.name = phone + '手机用户'
                # account.group_id = 3
                account.save()
                return Response({"message": "ok", "errorCode": 0})
            if email:
                if not email_re.match(email):
                    return Response({"message": "邮箱格式错误", "errorCode": 2, "data": {}})
                # if not captcha:
                #     return Response({"message": "验证码已过期", "errorCode": 2})
                # if '123456' != captcha:
                #     return Response({"message": "验证码错误", "errorCode": 2})
                account_check = User.objects.filter(email=email, is_delete=False)
                if account_check:
                    return Response({"message": "用户已经存在", "errorCode": 2})
                account = User()
                account.email = email
                # account.password = create_password(password)
                # 明文密码
                account.password = password
                account.name = email + '邮箱用户'
                # account.group_id = 3
                account.save()
                return Response({"message": "ok", "errorCode": 0})
        except Exception as e:
            print(e)
            return Response({"message": "未知错误", "errorCode": 1, "data": {}})




class UserInfo(APIView):
    # 加上用户验证 携带正确token时就会有user，否则就是AnonymousUser 就是没有用户的状态
    authentication_classes = (JWTAuthentication,)
    def get(self,request):
        request_log(request)
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            user = User.objects.filter(id=request.user.id,is_delete=False).first()
            serializer_user_data = UserSerializer(user)
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            json_data['data'] = serializer_user_data.data
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({"message": "未知错误", "errorCode": 1, "data": {}})

            


"""
class AddressViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id','region','user','receive_name','receive_phone','detail_addr','is_default','sort')
class AddressView(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    serializer_class = AddressViewSerializer
    def get(self,request):
        '''
        获取地址信息接口
        无需登录便可访问
        参数：
        id 传入id返回该条详细数据；否则返回全部数据
        page 页码
        page_size 每页数据量
        '''
        request_log(request)
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            group_id = request.user.group.id
            print('用户组ID：',group_id)
            # if group_id == 4:
            my_queryset = Address.objects.filter(user_id=request.user.id).order_by('sort','-created')
            pagination_clas = SchoolShopPagination()
            page_list = pagination_clas.paginate_queryset(queryset=my_queryset,request=request,view=self)
            serializer = AddressSerializer(instance=page_list, many=True)
            json_data['data'] = serializer.data
            json_data['tatol'] = len(my_queryset)
            # print(dir(status))
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({"message": "网络错误", "errorCode": 1, "data": {}})
    def post(self,request):
        '''
        新增地址信息接口
        需要登录才可访问
        参数：
        如接口示或联系后端人员
        '''
        request_log(request)
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            request.data['user'] = request.user.id
            print(request.data)
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            serializer.save()
            json_data['data'] = serializer.data
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({"message": "网络错误", "errorCode": 1, "data": {}})
    def patch(self,request):
        '''
        修改地址信息接口
        需要登录才可访问
        参数：
        如接口示或联系后端人员
        '''
        request_log(request)
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            id = request.data.get('id')
            if not id:
                return Response({"message": "id为必要字段", "errorCode": 2, "data": {}})
            item = Address.objects.filter(id=id).first()
            if not item:
                return Response({"message": "数据不存在或已经被删除", "errorCode": 2, "data": {}})
            request.data['user'] = request.user.id
            print(request.data)
            serializer = self.get_serializer(item,data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            serializer.save()
            json_data['data'] = serializer.data
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({"message": "网络错误", "errorCode": 1, "data": {}})
    def delete(self,request):
        '''
        删除地址信息接口
        需要登录才可以访问
        参数：
        如接口示或联系后端人员
        '''
        request_log(request)
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            id = request.data.get('id')
            if not id:
                return Response({"message": "id为必要字段", "errorCode": 2, "data": {}})
            item = Address.objects.filter(id=id).first()
            if not item:
                return Response({"message": "数据不存在或已经被删除", "errorCode": 2, "data": {}})
            item.delete()
            return Response(json_data)
        except Exception as e:
            print(e)
            return Response({"message": "网络错误", "errorCode": 1, "data": {}})
"""