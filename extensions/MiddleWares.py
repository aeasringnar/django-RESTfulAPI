import re
import time
import logging
from decimal import Decimal
from django.conf import settings
from django.db import connection
from django.http import QueryDict
from django.shortcuts import render
from django.core.cache import cache, caches
from django.utils.deprecation import MiddlewareMixin
from django.http.response import HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponse
from rest_framework import utils, status
from rest_framework.response import Response
from utils.Ecb import ECBCipher
'''
0 没有错误
1 未知错误  针对此错误  线上版前端弹出网络错误等公共错误
2 前端弹窗错误(包括：字段验证错误、自定义错误、账号或数据不存在、提示错误)
'''


class PUTtoPATCHMiddleware(MiddlewareMixin):
    '''将 put 请求转为 patch 请求 中间件'''
    
    def process_request(self, request):
        if request.method == 'PUT':
            request.method = 'PATCH'


class LogMiddleware(MiddlewareMixin):
    '''日志中间件'''
    
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
        logging.error('发生错误的请求地址：{}；错误原因：{}；错误详情：'.format(request.path, str(exception)))
        logging.exception(exception)
        return JsonResponse({"message": "An unexpected view error occurred: %s" % exception.__str__(), "errorCode": 1, "data": {}})
    
    def process_response(self, request, response):
        if settings.SHOWSQL:
            for sql in connection.queries:
                logging.debug(sql)
        return response


class PermissionMiddleware(MiddlewareMixin):
    '''接口加密中间件'''
    
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
                if not target_key: return JsonResponse({"message": "非法访问！已禁止操作！" , "errorCode": 10, "data": {}})
                # 解密成功后
                # 设置一个redis 记录当前时间戳
                time_int = int(time.time()) # 记录秒
                target_time, backend_key, random_str = target_key.split('+')
                if backend_key not in settings.DISPATCH_KEYS: return JsonResponse({"message": "非法访问！已禁止操作！" , "errorCode": 10, "data": {}})
                if (time_int - int(int(target_time) / 1000)) > settings.INTERFACE_TIMEOUT:
                    logging.info('发现秘钥被多次使用，应当记录ip加入预备黑名单。')
                    return JsonResponse({"message": "非法访问！已禁止操作！" , "errorCode": 10, "data": {}})
                cache.set(auth_key, "true", timeout=settings.INTERFACE_TIMEOUT)
                pass
            else:
                return JsonResponse({"message": "接口秘钥未找到！禁止访问！" , "errorCode": 10, "data": {}})


class DevelopSecurityInterFaceMiddleware(MiddlewareMixin):
    '''开发安全中间件，禁止非IP白名单的地址访问'''
    
    def process_request(self, request):
        white_ips = ['150.158.55.39', '35.227.152.73', '39.182.53.220', '127.0.0.1', '39.182.53.138', '115.236.184.202', '39.182.53.102']
        white_list = []
        white_ips += white_list
        rip = request.META.get('REMOTE_ADDR')
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if (rip not in white_ips and ip not in white_ips):
            return JsonResponse({"message": "bad request." , "errorCode": 11, "data": {}}, status=400)


class FormatReturnJsonMiddleware(MiddlewareMixin):
    '''格式化 response 中间件'''
    
    def process_response(self, request, response):
        try:
            # print('-'*128)
            # print(response.reason_phrase)
            # print(type(response))
            # print(dir(response))
            if isinstance(response, HttpResponseNotFound): 
                return JsonResponse({"message": response.reason_phrase, "errorCode": 2,"data": {}}, status=response.status_code)
            if isinstance(response, HttpResponseServerError): 
                return JsonResponse({"message": response.reason_phrase, "errorCode": 1,"data": {}}, status=response.status_code)
            if response.status_code == 204 : 
                return JsonResponse({"message": 'delete success', "errorCode": 0,"data": {}}, status=status.HTTP_200_OK)
            # print('-'*128)
        except Exception as e:
            logging.exception(e)
        return response
