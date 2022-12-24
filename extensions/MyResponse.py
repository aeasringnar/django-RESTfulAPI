from rest_framework.response import Response


class MyJsonResponse:
    
    def __init__(self, res_data: dict={}, status: int=200, headers=None) -> None:
        self.__res_format = {
            "msg": 'ok',
            "code": 0,
            "data": {}
        }
        self.__status = status
        self.__headers = headers
        if res_data:
            self.__res_format.update(res_data)
    
    def update(self, status:int = None, **kwargs):
        self.__res_format.update(kwargs)
        if status:
            self.__status = status
    
    @property
    def data(self):
        return Response(data=self.__res_format, status=self.__status, headers=self.__headers)