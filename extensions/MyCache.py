from typing import *
import pickle
from utils.RedisLockNew import RedisLock
from utils.RedisCli import RedisCli
import logging
import hashlib
from .MyResponse import MyJsonResponse
'''
装饰器类的第一种写法：__call__ 这个魔术方法，这个方法可以使类实例化后的对象可以像函数一样被调用，然后在这里直接接受被装饰的函数，
    这种方式在使用装饰器类时，是必须带括号的，也就是装饰器类是要被实例化的。具体实现如下
缓存方案：
    如何初始化缓存版本号：
        考虑在项目初始化时通过某些方法来初始化缓存版本号
        在项目初始化的时候，将所有路由进行初始化缓存版本号
        需要一个缓存版本号的服务类
        可以根据path查找缓存版本号
        可以更新缓存版本号
        可以初始化缓存版本号
        本质上是一个操作Redis缓存哈希表的操作类
    缓存装饰器：
        接收参数：
        cache_type 读缓存或写缓存
        cache_time 缓存的有效期 以秒为单位
        block 并发获取缓存时是否阻塞
        time_out 阻塞的超时时间
        retry 重试次数 
'''


class RedisCacheForDecoratorV1:
    
    def __init__(self, cache_type: str, cache_timeout: int, is_public: bool) -> None:
        '''装饰器类同样是一个类，它拥有类的特性，因此我们可以在装饰时设定一些参数，方便在装饰器中做一些特殊操作'''
        self._redis = RedisCli()
        self._cache_type = cache_type
        self._cache_timeout = cache_timeout
        self._is_public = is_public
        
    def __call__(self, func: Callable) -> Callable:
        '''使类实例化后的对象可以直接被当做函数调用，入参就是调用使传入的参数，利用这个可以实现装饰器类，入参就是要装饰的函数'''
        def warpper(re_self, request, *args: Any, **kwds: Any) -> Any:
            '''进行缓存计算或进行变更操作'''
            path_key = request.path
            operate_lock = RedisLock(self._redis.coon, path_key, self._cache_type)
            locked = operate_lock.acquire(timeout=30)
            if not locked:
                return MyJsonResponse({"message": "其他用户正在操作，请稍候重试", "errorCode": 2}, 400)
            res = func(*args, **kwds)
            return res
        return warpper
    
    def sign_hash(self, payload: str) -> str:
        h = hashlib.sha256()
        h.update(payload.encode(encoding='utf8'))
        return h.hexdigest()
