from rest_framework.response import Response
from rest_framework import utils
import json, os, copy, re, jwt, time
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
import urllib
from django.http import QueryDict, HttpResponse, JsonResponse
from django.http.response import HttpResponseNotFound, HttpResponseServerError
from django.conf import settings
from django.core.cache import cache
from utils.utils import jwt_decode_handler,jwt_encode_handler,jwt_payload_handler,jwt_payload_handler,jwt_response_payload_handler, jwt_get_user_id_from_payload_handler
from utils.web3utils import Web3Utils
from apps.user.models import User
from utils.services import NFTUitls
from utils.Ecb import ECBCipher
from django.db import connection
import logging
from django.core.cache import caches
from decimal import Decimal
'''
0 没有错误
1 未知错误  针对此错误  线上版前端弹出网络错误等公共错误
2 前端弹窗错误(包括：字段验证错误、自定义错误、账号或数据不存在、提示错误)
'''


class PUTtoPATCHMiddleware(MiddlewareMixin):
    '''
    将 put 请求转为 patch 请求 中间件
    '''
    def process_request(self, request):
        if request.method == 'PUT':
            request.method = 'PATCH'


class LogMiddleware(MiddlewareMixin):
    '''
    日志中间件
    '''
    def process_request(self, request):
        try:
            logging.info('************************************************* 下面是新的一条日志 ***************************************************')
            logging.info('拦截请求的地址：%s；请求的方法：%s' % (request.path, request.method))
            logging.info('==================================== headers 头信息 ====================================================')
            for key in request.META:
                if key[:5] == 'HTTP_':
                    logging.debug('%s %s' % (str(key), str(request.META[key])))
            logging.debug('%s %s' % ('Content-Type', str(request.META['CONTENT_TYPE'])))
            logging.info('代理IP：%s' % request.META.get('REMOTE_ADDR'))
            logging.info('真实IP：%s' % request.META.get('HTTP_X_FORWARDED_FOR'))   # HTTP_X_REAL_IP
            logging.info('==================================== request body信息 ==================================================')
            logging.info('params参数：%s' % request.GET)
            if request.content_type in ('application/json', 'text/plain', 'application/xml'):
                if request.path not in ('/callpresell/', ):
                    logging.info('body参数：%s' % request.body.decode())
            if request.content_type in ('multipart/form-data', 'application/x-www-form-urlencoded'):
                logging.info('是否存在文件类型数据：%s', bool(request.FILES))
                logging.info('data参数：%s', request.POST)
            logging.info('================================== View视图函数内部信息 ================================================')
        except Exception as e:
            logging.error('未知错误：%s' % str(e))
            return JsonResponse({"message": "请求日志输出异常：%s" % e, "errorCode": 1, "data": {}})

    def process_exception(self, request, exception):
        logging.error('发生错误的请求地址：%s；错误原因：%s；错误详情：' % (request.path, str(exception)))
        logging.exception(exception)
        return JsonResponse({"message": "An unexpected view error occurred: %s" % exception.__str__(), "errorCode": 1, "data": {}})
    
    def process_response(self, request, response):
        if settings.SHOWSQL:
            for sql in connection.queries:
                logging.debug(sql)
        return response



class PermissionMiddleware(MiddlewareMixin):
    '''
    权限 加密中间件
    '''
    def process_view(self, request):
        white_paths = ['/wechat/wxnotifyurl', '/', '/__debug__/', '/__debug__', '/favicon.ico']
        if request.path not in white_paths and not re.match(r'/swagger.*', request.path, re.I) and not re.match(r'/redoc/.*', request.path, re.I) and not re.match(r'/export.*', request.path, re.I):
            # print('查看authkey',request.META.get('HTTP_INTERFACEKEY'))
            auth_key = request.META.get('HTTP_INTERFACEKEY') # key顺序必须符合要求：毫秒时间戳+后端分配的key+32位随机字符串(uuid更佳)
            if auth_key:
                # print('查看秘钥：', cache.get(auth_key))
                if cache.get(auth_key):
                    logging.info('发现秘钥被多次使用，应当记录ip加入预备黑名单。')
                    return JsonResponse({"message": "非法访问！已禁止操作！" , "errorCode": 10, "data": {}})
                # 先解密
                target_obj = ECBCipher(settings.INTERFACE_KEY)
                target_key = target_obj.decrypted(auth_key)
                # 无法解密时直接禁止访问
                if not target_key:
                    return JsonResponse({"message": "非法访问！已禁止操作！" , "errorCode": 10, "data": {}})
                # 解密成功后
                # 设置一个redis 记录当前时间戳
                time_int = int(time.time()) # 记录秒
                target_time, backend_key, random_str = target_key.split('+')
                if backend_key not in settings.DISPATCH_KEYS:
                    return JsonResponse({"message": "非法访问！已禁止操作！" , "errorCode": 10, "data": {}})
                if (time_int - int(int(target_time) / 1000)) > settings.INTERFACE_TIMEOUT:
                    logging.info('发现秘钥被多次使用，应当记录ip加入预备黑名单。')
                    return JsonResponse({"message": "非法访问！已禁止操作！" , "errorCode": 10, "data": {}})
                cache.set(auth_key, "true", timeout=settings.INTERFACE_TIMEOUT)
                pass
            else:
                return JsonResponse({"message": "接口秘钥未找到！禁止访问！" , "errorCode": 10, "data": {}})


class PermissionCallBackMiddleware(MiddlewareMixin):
    '''
    回调接口中间件，杜绝黑名单IP的访问
    '''
    def process_view(self, request, callback, callback_args, callback_kwargs):
        white_ips = ['150.158.55.39', '35.227.152.73', '39.182.53.220', '127.0.0.1', '39.182.53.138', '115.236.184.202']
        white_list = NFTUitls().white_list(list_type='1')
        white_ips += white_list
        rip = request.META.get('REMOTE_ADDR')
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if request.path in ('/callpresell/', ) and (rip not in white_ips and ip not in white_ips):
            return JsonResponse({"message": "this ip not allow." , "errorCode": 10, "data": {}})
        if request.path in ('/airport/', '/extract/', ):
            cache = caches['cache_redis']
            remote_addr = request.META.get('HTTP_X_REAL_IP') if not request.META.get('REMOTE_ADDR') else request.META.get('REMOTE_ADDR')
            if cache.get(remote_addr) and int(cache.get(remote_addr)) > settings.DAY_HZ:
                return JsonResponse({"message": "bad request." , "errorCode": 10, "data": {}})


class SecurityInterFaceMiddleware(MiddlewareMixin):
    '''
    安全接口中间件，阻挡异常IP的请求
    '''
    def process_request(self, request):
        cache = caches['cache_redis']
        remote_addr = request.META.get('HTTP_X_REAL_IP') if not request.META.get('REMOTE_ADDR') else request.META.get('REMOTE_ADDR')
        freeze_key = 'notfound-freeze-%s' % remote_addr
        if cache.get(freeze_key):
            return JsonResponse({"message": 'Malicious access has been detected. IP has been blocked.', "errorCode": 3,"data": {}}, status=status.HTTP_400_BAD_REQUEST)
        

class DevelopSecurityInterFaceMiddleware(MiddlewareMixin):
    '''
    开发安全中间件，禁止非IP白名单的地址访问
    '''
    def process_request(self, request):
        white_ips = ['150.158.55.39', '35.227.152.73', '39.182.53.220', '127.0.0.1', '39.182.53.138', '115.236.184.202', '39.182.53.102']
        white_list = NFTUitls().white_list(list_type='1')
        white_ips += white_list
        rip = request.META.get('REMOTE_ADDR')
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if (rip not in white_ips and ip not in white_ips):
            return JsonResponse({"message": "bad request." , "errorCode": 11, "data": {}}, status=400)


class FormatReturnJsonMiddleware(MiddlewareMixin):
    '''
    格式化 response 中间件
    '''
    def process_response(self, request, response):
        try:
            # print('-'*128)
            # print(response.reason_phrase)
            # print(type(response))
            # print(dir(response))
            if isinstance(response, HttpResponseNotFound) :
                cache = caches['cache_redis']
                remote_addr = request.META.get('HTTP_X_REAL_IP') if not request.META.get('REMOTE_ADDR') else request.META.get('REMOTE_ADDR')
                key = 'notfound-%s' % remote_addr
                freeze_key = 'notfound-freeze-%s' % remote_addr
                if cache.get(key):
                    cache.incr(key)
                else:
                    cache.set(key, 1, 60*60*24)
                if cache.get(key) >= settings.NOTFOUND_HZ:
                    cache.set(freeze_key, 1, 60*60*24*7)
                return JsonResponse({"message": response.reason_phrase, "errorCode": 2,"data": {}}, status=response.status_code)
            if isinstance(response, HttpResponseServerError) : return JsonResponse({"message": response.reason_phrase, "errorCode": 1,"data": {}}, status=response.status_code)
            if response.status_code == 204 : return JsonResponse({"message": 'delete success', "errorCode": 0,"data": {}}, status=status.HTTP_200_OK)
            # print('-'*128)
        except Exception as e:
            logging.exception(e)
        return response


class BlockUserMiddleware(MiddlewareMixin):
    '''
    冻结用户中间件 暂时弃用 2022-05-14
    '''
    def process_view(self, request, callback, callback_args, callback_kwargs):
        wilte_path = ('/login/', '/indexSpotGoods/', '/indexConfDict/', '/createPopularizeAward/', '/adminlogin/', '/callbuyom/', '/uploadForPro/')
        if request.path in wilte_path:
            pass
        elif request.META.get('HTTP_AUTHORIZATION'):
            if ' ' not in request.META.get('HTTP_AUTHORIZATION'):
                return JsonResponse({"message": 'Token is not valid.' , "errorCode": 2, "data": {}})
            token = (request.META.get('HTTP_AUTHORIZATION').split(' '))[1]
            try:
                payload = jwt_decode_handler(token)
                user_id =  jwt_get_user_id_from_payload_handler(payload)
                if not user_id:
                    return JsonResponse({"message": "The user does not exist." , "errorCode": 2, "data": {}})
                now_user = User.objects.values('id', 'is_freeze').filter(id=user_id).first()
                if not now_user:
                    return JsonResponse({"message": "The user does not exist." , "errorCode": 2, "data": {}})
                if now_user.get('is_freeze'):
                    return JsonResponse({"message": "Account frozen!", "errorCode": 2, "data": {}})
            except jwt.ExpiredSignature:
                return JsonResponse({"message": 'Token expired.' , "errorCode": 2, "data": {}})
            except jwt.DecodeError:
                return JsonResponse({"message": 'Token is not valid.' , "errorCode": 2, "data": {}})
            except jwt.InvalidTokenError as e:
                return JsonResponse({"message": "An unexpected view error occurred: %s" % e, "errorCode": 1, "data": {}})
            
            
class CheckTokenVersionAndUserFreezeMiddleware(MiddlewareMixin):
    '''
    检查token版本和用户是否冻结中间件，目的基本一样，都是检查大部分鉴权接口中，token的版本和用户是否冻结
    只用一个中间件，可以提升性能
    '''
    def process_view(self, request, callback, callback_args, callback_kwargs):
        white_path = ('/login/', '/indexSpotGoods/', '/indexConfDict/', '/myAward/', '/createPopularizeAward/', '/adminlogin/', '/callTransfer/', '/uploadForPro/')
        if request.path in white_path:
            pass
        elif request.META.get('HTTP_AUTHORIZATION'):
            if ' ' not in request.META.get('HTTP_AUTHORIZATION'):
                return JsonResponse({"message": 'Token is not valid.' , "errorCode": 2, "data": {}})
            token = (request.META.get('HTTP_AUTHORIZATION').split(' '))[1]
            try:
                payload = jwt_decode_handler(token)
                user_id =  jwt_get_user_id_from_payload_handler(payload)
                if not user_id:
                    return JsonResponse({"message": "The user does not exist." , "errorCode": 2, "data": {}})
                now_user = User.objects.values('id', 'token_version', 'is_freeze').filter(id=user_id).first()
                if not now_user:
                    return JsonResponse({"message": "The user does not exist." , "errorCode": 2, "data": {}})
                if now_user.get('token_version') != payload.get('version'):
                    return JsonResponse({"message": "The token is implemented", "errorCode": 2, "data": {}})
                if now_user.get('is_freeze'):
                    return JsonResponse({"message": "Account frozen!", "errorCode": 2, "data": {}})
            except jwt.ExpiredSignature:
                return JsonResponse({"message": 'Token expired.' , "errorCode": 2, "data": {}})
            except jwt.DecodeError:
                return JsonResponse({"message": 'Token is not valid.' , "errorCode": 2, "data": {}})
            except jwt.InvalidTokenError as e:
                return JsonResponse({"message": "An unexpected view error occurred: %s" % e, "errorCode": 1, "data": {}})