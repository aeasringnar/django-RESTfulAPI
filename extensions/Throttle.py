from rest_framework.throttling import BaseThrottle
from django.conf import settings
from utils.RedisCli import RedisCli


class VisitThrottle(BaseThrottle):
    '''自定义频率限制类'''
    def __init__(self):
        self.history = None
        self.cache = RedisCli()

    def allow_request(self, request, view):
        remote_addr = request.META.get('HTTP_X_REAL_IP') if not request.META.get('REMOTE_ADDR') else request.META.get('REMOTE_ADDR')
        # print('请求的IP：', remote_addr)
        # print('请求的路径：', request.path)
        # print('请求的方法：', request.method)
        if request.user and request.user.id:
            remote_addr = 'user%s' % request.user.id
        self.visit_key = remote_addr + request.path
        # print('构造请求的key', self.visit_key)
        counts = self.cache.coon.get(self.visit_key)
        if not counts:
            self.cache.coon.set(self.visit_key, 1, 60, nx=True)
            return True
        if int(counts.decode()) >= settings.MINUTE_HZ:
            return False
        self.cache.coon.incr(self.visit_key)
        self.cache.coon.expire(self.visit_key, 60)
        return True

    def wait(self):
        es = self.cache.coon.pttl(self.visit_key) # 以毫秒为单位返回键的剩余过期时间
        es = (int(es) / 1000)
        return es
