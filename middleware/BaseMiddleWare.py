from rest_framework.response import Response
from rest_framework import utils
import json
import os
import copy
import re
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
import urllib
from django.http import QueryDict, HttpResponse, JsonResponse


class PrintLogMiddleware(MiddlewareMixin):

    def process_request(self, request):
        print('************************************************* 下面是新的一条日志 ***************************************************')
        print('拦截请求的地址：', request.path, '请求的方法：', request.method)
        print('==================================== headers 头信息 ====================================================')
        for key in request.META:
            if key[:5] == 'HTTP_':
                print(key, request.META[key])
        print('==================================== request body信息 ==================================================')
        print('params参数：', request.GET)
        if request.path == '/uploadfile/':
            print('body参数：', '文件类型')
        else:
            print('body参数：', request.body.decode())
            if 'application/x-www-form-urlencoded' in request.META['CONTENT_TYPE']:
                print('body参数：', urllib.parse.unquote(request.body.decode()))
        print('================================== View视图函数内部信息 ================================================')

    def process_exception(self, request, exception):
        print('发生错误的请求地址：', request.path, '。错误原因：',exception)
        return JsonResponse({"message": "出现了无法预料的view视图错误：%s" % exception.__str__(), "errorCode": 1, "data": {}})



class FormatReturnJsonMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if hasattr(self, 'process_request'):
                response = self.process_request(request)
            if not response:
                response = self.get_response(request)
            if hasattr(self, 'process_response'):
                response = self.process_response(request, response)
            if request.method == 'DELETE':
                print(response.data)
                if response.status_code == 204:
                    response.data = {"message": '删除成功', "errorCode": 0, "data": {}}
                else:
                    if response.data.get('detail'):
                        data = {"message": response.data.get('detail'), "errorCode": 1, "data": {}}
                    elif response.data.get('message'):
                        data = response.data
                    else:
                        data = {"message": 'error', "errorCode": 1, "data": response.data}
                    response.data = data
                response.status_code = 200
                response._is_rendered = False
                response.render()
            else:
                if request.path is not '/' and not re.match(r'/swagger.*', request.path, re.I) and not re.match(r'/redoc/.*', request.path, re.I) and not re.match(r'/export.*', request.path, re.I):
                    # 适配不分页返回数据的格式化
                    if type(response.data) == utils.serializer_helpers.ReturnList:
                        data = {"message": 'ok', "errorCode": 0,"data": response.data}
                        response.data = data
                    if response.data.get('detail'):
                        data = {"message": response.data.get('detail'), "errorCode": 1, "data": {}}
                        response.data = data
                    elif response.status_code > 200 and response.status_code <= 299:
                        data = {"message": 'ok', "errorCode": 0,"data": response.data}
                        response.data = data
                    elif response.status_code >= 400 and response.status_code <= 499:
                        if response.data.get('message'):  # 兼容APIView返回data的设置
                            pass
                        else:
                            data = {"message": str(response.data), "errorCode": 1,"data": response.data}
                            response.data = data
                    else:
                        if response.data.get('message'):  # 兼容APIView返回data的设置
                            pass
                        elif response.data.get('count') != None:  # 兼容分页返回data的设置
                            response.data['errorCode'] = 0
                            response.data['message'] = 'ok'
                        else:
                            data = {"message": 'ok', "errorCode": 0,
                                    "data": response.data}
                            response.data = data
                    response.status_code = 200
                    response._is_rendered = False
                    response.render()
        except Exception as e:
            print('发生错误：', e)
        return response