from typing import *
import pickle
from utils.RedisLockNew import RedisLock
from utils.RedisCli import RedisCli, RedisHash
from utils.Utils import NormalObj
import logging
import hashlib
from .MyResponse import MyJsonResponse
from rest_framework.response import Response
from django.conf import settings
from functools import wraps
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


class CacheVersionControl:
    '''缓存版本号操作类'''
    
    def __init__(self, paths: List[str]=None) -> None:
        self._key = f"cache_version+{NormalObj.to_sha256(settings.SECRET_KEY)}"
        self._cache_dict = RedisHash(self._key)
        self._paths = paths
    
    def update(self, key: str) -> bool:
        '''更新某个path的缓存版本号'''
        data = self._cache_dict.get(key, 0)
        data += 1
        return bool(self._cache_dict.setdefault(key, data))
    
    def get(self, key: str) -> int:
        return self._cache_dict.get(key)
    
    def init_data(self):
        '''初始化缓存版本数据'''
        if not self._cache_dict.is_empty:
            self._cache_dict.clear()
        for path in self._paths:
            self._cache_dict[path] = 0
    
    def flush_date(self):
        '''销毁缓存版本数据'''
        self._cache_dict.clear()


class RedisCacheForDecoratorV1:
    '''第一版本的缓存装饰器类'''
    
    def __init__(self, cache_type: str, cache_timeout: int=300) -> None:
        '''装饰器类同样是一个类，它拥有类的特性，因此我们可以在装饰时设定一些参数，方便在装饰器中做一些特殊操作'''
        self._redis = RedisCli()
        self._cache_type = cache_type
        self._cache_timeout = cache_timeout
        self._is_public = True
        self._response = MyJsonResponse()
        
    def __call__(self, func: Callable) -> Callable:
        '''使类实例化后的对象可以直接被当做函数调用，入参就是调用使传入的参数，利用这个可以实现装饰器类，入参就是要装饰的函数'''
        @wraps(func)
        def warpper(re_self, request, *args: Any, **kwds: Any) -> Any:
            '''进行缓存计算或进行变更操作'''
            try:
                if hasattr(re_self, 'is_public'):
                    self._is_public = getattr(re_self, 'is_public')
                path_key = request.path
                operate_lock = RedisLock(self._redis.coon, path_key, self._cache_type)
                locked = operate_lock.acquire(timeout=30)
                if not locked:
                    self._response.update(status=400, message="Another user is operating, please try again later.", erroCode=2)
                    return self._response.data
                # 加锁成功就执行业务逻辑
                # 判断是写操作的话，直接执行方法，方法执行完毕后进行更新缓存版本号
                if self._cache_type == 'w':
                    res = func(re_self, request, *args, **kwds)
                    # 更新缓存版本号的逻辑
                    CacheVersionControl().update(request.path)
                    # 释放操作锁
                    operate_lock.release()
                    return res
                # 否则进行缓存相关的逻辑操作
                '''
                todo list
                1、计算缓存的key key = 接口path的hash + 请求的参数hash(如果is_public为假，需要加入token来计算哈希) + 接口的缓存版本号
                2、根据缓存key 来加锁，设置超时时间，超时后先在判断一次缓存是否被生成：如果生成，那就返回缓存结果，否则返回超时。
                3、如果加锁成功，先判断缓存是否存在，如果不存在就进行 查库 设置缓存，返回。
                这样能解决：
                    1、高并发下的热点缓存失效，导致的数据库压力激增。
                    2、高并发下的大并发创建缓存问题。
                '''
                payload = f"{request.path}+{request.GET}+{CacheVersionControl().get(request.path)}"
                cache_base_key = NormalObj.to_sha256(payload) if self._is_public else NormalObj.to_sha256(f"{payload}+{request.user}")
                target_cache_key = cache_base_key+':cache'
                cache_lock = RedisLock(self._redis.coon, cache_base_key+':lock', 'w')
                locked = cache_lock.acquire(timeout=20)
                if not locked:
                    # 假设没有获得锁，那么就会因为超时而退出，此时再查一次缓存，如果存在就返回，否则就返回有人在操作。
                    cache_val = self._redis.coon.get(target_cache_key)
                    if cache_val:
                        content, status, headers = pickle.loads(cache_val)
                        return Response(data=content, status=status, headers=headers)
                    self._response.update(status=400, message="Another user is operating, please try again later.", erroCode=2)
                    return self._response.data
                # 如果加锁成功，就先查缓存，没有就落库并设置缓存
                cache_val = self._redis.coon.get(target_cache_key)
                if not cache_val:
                    response = func(re_self, request, *args, **kwds)
                    
                    if response.status_code == 200:
                        if hasattr(response, '_headers'):
                            headers = response._headers.copy()
                        else:
                            headers = {k: (k, v) for k, v in response.items()}
                        response_triple = (
                            response.data,
                            response.status_code,
                            headers
                        )
                        self._redis.coon.setex(target_cache_key, self._cache_timeout, pickle.dumps(response_triple))
                    cache_lock.release()
                    return response
                content, status, headers = pickle.loads(cache_val)
                cache_lock.release()
                return Response(data=content, status=status, headers=headers)
            except Exception as e:
                logging.exception(e)
                self._response.update(status=500, message=f"MyCache Error: {e}", erroCode=2)
                return self._response.data
        return warpper
