import uuid, os, sys, requests, json, re, time, datetime, random, hashlib, hmac, base64, xml, subprocess, threading
from django.db.models import F, Q
from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.forms.models import model_to_dict
# 官方JWT
# from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler ,jwt_response_payload_handler
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
# 缓存配置
from django.core.cache import cache
# 自定义的JWT配置 公共插件
from utils.utils import jwt_decode_handler,jwt_encode_handler,jwt_payload_handler,jwt_payload_handler,jwt_response_payload_handler,google_otp,VisitThrottle,getDistance,NormalObj, \
    wechat_mini_login, wechat_app_login, get_wechat_token
from utils.WeChatCrypt import WXBizDataCrypt
from utils.AliMsg import create_code, SendSmsObject
from utils.jwtAuth import JWTAuthentication
from utils.pagination import Pagination
from utils.permissions import JWTAuthPermission, AllowAllPermission, BaseAuthPermission
from .models import *
from .serializers import *
from .filters import *
from functools import reduce
from urllib.parse import unquote_plus
from django.conf import settings
'''
serializers 常用字段
name = serializers.CharField(required=False, label='描述', max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
name = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
name = serializers.FloatField(max_value=None, min_value=None)
name = serializers.IntegerField(max_value=None, min_value=None)
name = serializers.DateTimeField(format=api_settings.DATETIME_FORMAT, input_formats=None)
name = serializers.DateField(format=api_settings.DATE_FORMAT, input_formats=None)
name = serializers.BooleanField()
name = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=100))
name = serializers.DictField(child=<A_FIELD_INSTANCE>, allow_empty=True)  DictField(child=CharField())
(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet, generics.GenericAPIView)
Q(name__icontains=keyword) 内部是like模糊搜索
__gt 大于 
__gte 大于等于
__lt 小于 
__lte 小于等于
__in 在某某范围内
is null / is not null 为空/非空
.exclude(age=10) 查询年龄不为10的数据
'''
# 测试的cache 所用的包 drf-extensions
# from rest_framework_extensions.cache.mixins import CacheResponseMixin # CacheResponseMixin使用在viewset里可以针对某些请求进行缓存
# from rest_framework_extensions.cache.decorators import (
#     cache_response
# )


# 后台登录
class LoginView(generics.GenericAPIView):
    serializer_class = LoginViewSerializer
    def post(self, request):
        '''
        后台登录接口
        '''
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 2, "data": {}})
            data = (serializer.data)
            username = data.get('username')
            password = data.get('password')
            user = User.objects.filter(Q(username=username) | Q(mobile=username) | Q(email=username)).first()
            if not user:
                return Response({"message": "用户不存在", "errorCode": 2, "data": {}})
            if user.group.group_type in ['NormalUser']:
                return Response({"message": "非法登录，不是后台用户！", "errorCode": 2, "data": {}})
            if user.is_freeze in ['1', 1]:
                return Response({"message": "账号被冻结，无法登录。", "errorCode": 2, "data": {}})
            if user.password == password:
                token_data = jwt_response_payload_handler(jwt_encode_handler(payload = jwt_payload_handler(user)), user, request)
                user.update_time = datetime.datetime.now()
                user.save()
                return Response({"message": "登录成功", "errorCode": 0, "data": token_data})
            else:
                return Response({"message": "密码错误", "errorCode": 2, "data": {}})
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 微信小程序登
class WeChatMiniLoginView(generics.GenericAPIView):
    serializer_class = WeChatLoginViewSerializer
    @transaction.atomic
    def post(self, request):
        '''
        微信小程序登录接口
        '''
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 2, "data": {}})
            print(serializer.data)
            code = serializer.data.get('code')
            userInfo = serializer.data.get('userInfo')
            encrypted_data = serializer.data.get('encrypted_data')
            iv = serializer.data.get('iv')
            # print(userInfo.get('avatarUrl'))
            # 调用微信登录获取openid
            open_id, union_id, session_key = wechat_mini_login(code)
            if type(open_id) == dict:
                return Response(open_id)
            # 测试绕过微信登录
            # open_id = 'asdfasdf21341cdfq345sderffggfwe45'
            # 根据openid查找用户
            we_user = User.objects.filter(open_id=open_id).first()
            if not union_id:
                pc_obj = WXBizDataCrypt(settings.WECHAT_MINI_APPID, session_key)
                union_id = pc_obj.decrypt(encrypted_data, iv).get('unionId')
            app_user = User.objects.filter(union_id=union_id).first()
            is_login = 1
            print('查看user',user)
            if we_user and app_user:
                if not we_user.union_id:
                    we_user.union_id = union_id
                    we_user.save()
                user = we_user
            elif we_user and not app_user:
                if not we_user.union_id:
                    we_user.union_id = union_id
                    we_user.save()
                user = we_user
            elif app_user and not we_user:
                if not app_user.open_id:
                    app_user.open_id = open_id
                    app_user.save()
                user = app_user
            else:
                is_login = 0
                user = User()
                user.group_id = 3
                user.open_id = open_id
                user.union_id = union_id
                user.nick_name = userInfo.get('nickName')
                user.avatar_url = userInfo.get('avatarUrl')
                user.gender = userInfo.get('gender')
                user.region = ' '.join([str(item) for item in [userInfo.get('country'), userInfo.get('province'), userInfo.get('city')] if item != None])
                user.save()
            token_data = jwt_response_payload_handler(jwt_encode_handler(payload = jwt_payload_handler(user)), user, request)
            token_data['is_login'] = is_login
            user.update_time = datetime.datetime.now()
            user.save()
            return Response({"message": "登录成功", "errorCode": 0, "data": token_data})
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 微信APP第三方登录
class WeChatAppLoginView(generics.GenericAPIView):
    serializer_class = WeChatAppLoginViewSerializer
    @transaction.atomic
    def post(self, request):
        '''
        微信APP第三方登录接口
        '''
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 2, "data": {}})
            # print(serializer.data)
            code = serializer.data.get('code')
            user_info = wechat_app_login(code)
            if user_info.get('errcode') and user_info.get('errcode') != 0:
                return Response(user_info)
            # 根据 unionid 查找用户
            user = User.objects.filter(union_id=user_info.get('unionid')).first()
            is_login = 0
            if not user:
                is_login = 1
                user = User()
                user.group_id = 3
                user.union_id = user_info.get('unionid')
                user.nick_name = user_info.get('nickname')
                user.avatar_url = user_info.get('headimgurl')
                user.gender = user_info.get('sex')
                user.region = ' '.join([str(item) for item in [user_info.get('country'), user_info.get('province'), user_info.get('city')] if item != None])
                user.save()
            token_data = jwt_response_payload_handler(jwt_encode_handler(jwt_payload_handler(user)), user, request)
            token_data['is_login'] = is_login
            user.update_time = datetime.datetime.now()
            user.save()
            return Response({"message": "登录成功", "errorCode": 0, "data": token_data})
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


class MobileLoginView(generics.GenericAPIView):
    serializer_class = MobileLoginSerializer
    def post(self, request):
        '''
        手机号快速登录接口
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 4, "data": {}})
            mobile = serializer.data.get('mobile')
            code = serializer.data.get('code')
            is_login = 1
            # 搜索用户
            user_obj = User.objects.filter(mobile=mobile).first()
            # 搜索缓存
            need_value = cache.get(mobile)
            if not need_value:
                return Response({"message": "验证码未找到，请重新发送后重试。", "errorCode": 2, "data": {}})
            if need_value != code:
                return Response({"message": "验证码错误。", "errorCode": 2, "data": {}})
            if not user_obj:
                is_login = 0
                # 1
                # user_obj = User()
                # user_obj.group_id = 3
                # user_obj.nick_name = mobile + '手机用户'
                # user_obj.save()
                # 2
                user_obj = User(group_id=3, nick_name=mobile + '手机用户', mobile=mobile)
                user_obj.save()
            token_data = jwt_response_payload_handler(jwt_encode_handler(jwt_payload_handler(user_obj)), user_obj, request)
            user_obj.update_time = datetime.datetime.now()
            user_obj.save()
            # 清除已经使用的验证码 防止验证码被盗用
            cache.delete(mobile)
            return Response({"message": "登录成功", "errorCode": 0, "data": {'token': token_data.get('token'), 'is_login': is_login}})
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 发送短信验证码
class MobileCodeView(generics.GenericAPIView):
    serializer_class = MobileFormSerializer
    def post(self, request):
        '''
        发送短信验证码接口
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": str(serializer.errors), "errorCode": 2, "data": {}})
            mobile = serializer.data.get('mobile')
            check_code = cache.get(mobile)
            if check_code:
                Response({"message": "验证码已经发送，请勿重复提交。", "errorCode": 2, "data": {}})
            random_code = create_code()
            send_obj = SendSmsObject(settings.ALI_KEY, settings.ALI_SECRET, settings.ALI_REGION, settings.ALI_SIGNNAME)
            return_msg = send_obj.send_code(settings.ALI_LOGOIN_CODE, mobile, random_code)
            if return_msg["Code"] != 'OK':
                json_data['message'] = '发送失败，请更换手机号或重新尝试。'
                json_data['errorCode'] = '2'
            # 设置缓存
            cache.set(mobile, random_code, timeout=5 * 60)
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 用户修改自己的用户信息视图
class WeChatUpdateUserViewset(mixins.UpdateModelMixin, GenericViewSet):
    '''
    update:更新用户信息
    '''
    authentication_classes = (JWTAuthentication,)
    permission_classes = [JWTAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = WeChatUpdateUserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


# 后台用户管理
class UserViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建用户
    retrieve:  检索某个用户
    update:  更新用户
    destroy:  删除用户
    list:  获取用户列表
    '''
    queryset = User.objects.filter(group__group_type__in=['SuperAdmin', 'Admin']).order_by('-create_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnUserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('username', 'mobile', 'email',)
    filter_fields = ('is_freeze', 'group', 'auth', )
    ordering_fields = ('id', 'update_time', 'create_time',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ['create']:
            return AddUserSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return ReturnUserSerializer


# 普通用户管理
class MemberViewset(mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    '''
    修改局部数据
    retrieve:  检索某个用户
    update:  更新用户
    list:  获取用户列表
    '''
    queryset = User.objects.filter(group__group_type='NormalUser').order_by('-create_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnMemberSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('username', 'mobile', 'email',)
    filter_fields = ('is_freeze', 'group', 'auth', )
    ordering_fields = ('id', 'update_time', 'create_time',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateMemberSerializer
        return ReturnMemberSerializer


# 测试导出Excel数据流
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
class UserDictExportViewset(XLSXFileMixin, ReadOnlyModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = ReturnUserSerializer
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [BaseAuthPermission, ]
    renderer_classes = (XLSXRenderer,)
    filename = 'my_export.xlsx'
    column_header = {
        'titles': [
            "Column_1_name",
            "Column_2_name",
            "Column_3_name",
        ],
    }


# 获取个人信息
class UserInfo(APIView):
    authentication_classes = (JWTAuthentication,)

    # 测试对返回的数据进行缓存
    # @cache_response()
    def get(self, request, *args, **kwargs):
        '''
        获取个人信息
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            user = User.objects.filter(id=request.user.id).first()
            user.bf_logo_time = user.update_time
            user.save()
            json_data['data'] = ReturnUserSerializer(user).data
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 后台权限接口
class AuthViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建权限
    retrieve:  检索某个权限
    update:  更新权限
    destroy:  删除权限
    list:  获取权限列表
    '''
    queryset = Auth.objects.all().order_by('-create_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ReturnAuthSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('auth_type',)
    ordering_fields = ('id', 'update_time', 'create_time',)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AddAuthSerializer
        return ReturnAuthSerializer