from rest_framework.views import exception_handler
from django.http import JsonResponse


def base_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if not response:
        if response.status_code == '204':
            response = JsonResponse({"message": '删除成功', "errorCode": 0, "data": {}}, status=response.status_code)
        else:
            response = JsonResponse({"message": 'ok', "errorCode": 0, "data": {}}, status=response.status_code)
    else:
        response = JsonResponse({"message": response.data.get('detail'), "errorCode": 0, "data": {}}, status=response.status_code)
    return response