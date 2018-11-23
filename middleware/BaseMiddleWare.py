from rest_framework.response import Response
import json,os
# 继承自一个文件
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
# 注意写完之后要在setings里面进行注册 在MIDDLEARE里面注册使用
class myMiddle(MiddlewareMixin):
    def process_request(self,request):
        print('===============================================下面是新的一条日志====================================================')
        print('拦截请求的地址：',request.path,'请求的方法：',request.method)
        print('====================================headers 头信息====================================================')
        for key in request.META:
            if key[:5] == 'HTTP_':
                print(key, request.META[key])
        # if request.body:
        #     print('====================================request body信息==================================================')
            # request_dic = json.loads(request.body, encoding='utf-8')
            # print(request_dic)

    def process_exception(self, request, exception):
        print('发生错误的请求地址', request.path, exception.__str__)
        return Response({"message": "出现了无法预料的view视图错误", "errorCode": 1, "data": {}})

    def process_response(self,request,response):
        # response_dic = json.loads(response.content,encoding='utf-8')
        print('====================================response 日志信息=================================================')
        if (type(response.content.decode('utf-8'))) == str:
            print(response.content.decode('utf-8'))
        return response
