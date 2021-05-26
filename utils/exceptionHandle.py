from rest_framework.views import exception_handler
from django.http import JsonResponse
import logging


def base_exception_handler(exc, context):
    '''
    用于处理drf的异常定制返回，目的是统一返回信息，只有drf出现异常时才会执行，其他情况不执行
    '''
    logging.debug('DRF主动提示异常')
    response = exception_handler(exc, context)
    if not response:
        pass
        # print('+' * 128)
        # print(exc)
        # print('+' * 128)
        # response = JsonResponse({"message": str(exc), "errorCode": 1, "data": {}})
    else:
        logging.debug(response.data)
        msg = ''
        for key in response.data:
            if key in ('detail', 'non_field_errors'):
                msg += '%s' % (';'.join(response.data[key])) if isinstance(response.data[key], list) else (response.data[key])
            else:
                msg += '%s：%s ' % (key, ';'.join(response.data[key]))
        code = 0 if response.status_code == 200 else 2
        return JsonResponse({"message": msg, "errorCode": code, "data": {}}, status=response.status_code)
    return response