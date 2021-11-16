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
from apps.user.models import User
from utils.ECB import ECBCipher
from django.db import connection
import logging

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
        return JsonResponse({"message": "出现了无法预料的view视图错误：%s" % exception.__str__(), "errorCode": 1, "data": {}})
    
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
            if isinstance(response, HttpResponseNotFound) : return JsonResponse({"message": response.reason_phrase, "errorCode": 2,"data": {}}, status=response.status_code)
            if isinstance(response, HttpResponseServerError) : return JsonResponse({"message": response.reason_phrase, "errorCode": 1,"data": {}}, status=response.status_code)
            if response.status_code == 204 : return JsonResponse({"message": '删除成功', "errorCode": 0,"data": {}}, status=response.status_code)
            # print('-'*128)
        except Exception as e:
            logging.exception(e)
        return response


class BlockUserMiddleware(MiddlewareMixin):
    '''
    冻结用户中间件
    '''
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.META.get('HTTP_AUTHORIZATION'):
            if ' ' not in request.META.get('HTTP_AUTHORIZATION'):
                return JsonResponse({"message": 'Token不合法' , "errorCode": 2, "data": {}})
            token = (request.META.get('HTTP_AUTHORIZATION').split(' '))[1]
            try:
                payload = jwt_decode_handler(token)
                user_id =  jwt_get_user_id_from_payload_handler(payload)
                if not user_id:
                    return JsonResponse({"message": "用户不存在！" , "errorCode": 2, "data": {}})
                now_user = User.objects.values('id', 'is_freeze').filter(id=user_id).first()
                if not now_user:
                    return JsonResponse({"message": "用户不存在！" , "errorCode": 2, "data": {}})
                if now_user.get('is_freeze'):
                    return JsonResponse({"message": "账户被冻结！", "errorCode": 2, "data": {}})
            except jwt.ExpiredSignature:
                return JsonResponse({"message": 'Token过期' , "errorCode": 2, "data": {}})
            except jwt.DecodeError:
                return JsonResponse({"message": 'Token不合法' , "errorCode": 2, "data": {}})
            except jwt.InvalidTokenError as e:
                return JsonResponse({"message": "出现了无法预料的view视图错误：%s" % e, "errorCode": 1, "data": {}})