from redis import StrictRedis
from datetime import datetime
import time
from enum import Enum
from typing import Optional, Tuple
'''
新版的分布式可充入读写锁
实现原理：
1、基本的分布式锁原理，通过设置redis的key nx 即如果key存在则创建，否则返回none，创建锁时增加过期时间参数，默认30秒
2、可以同个key的值加上锁类型，读锁或写锁 以及锁id(防止锁被别人释放) 加上加锁次数 目的是支持可重入的锁，当加锁次数为0时，释放锁
3、在加锁时增加timeout参数，毫秒值，如果有值那么表示加锁时，如果锁被人锁着，那么就进行重试等待 值表示等待的时间，为None时表示不阻塞，有锁时直接返回加锁失败。
4、使用上下文管理器，进入时加锁，离开时释放锁，
'''


class RedisLock:
    
    def __init__(self, redis_conn: StrictRedis, key: str, lock_id: str, lock_type: str='w', expire: int=30) -> None:
        '''锁的初始化
        args:
            redis_conn Redis连接对象
            key 锁的key
            lock_id 加锁的id
            lock_type 加锁的类型，可选值为 r 读锁 w 写锁，默认为写锁
            expire 锁的过期时间，单位为秒，默认为30秒
        '''
        if not isinstance(redis_conn, StrictRedis):
            raise ValueError("redis_conn is not StrictRedis")
        if not isinstance(lock_id, str):
            raise ValueError("lock_id need str type")
        if lock_type not in {'r', 'w'}:
            raise ValueError("lock_type is not allowed")
        if not isinstance(expire, int):
            raise ValueError("expire need int type")
        if expire < 0:
            raise ValueError("expire must large zero")
        if isinstance(key, str):
            raise ValueError("key need str type")
        self._conn = redis_conn
        self._key = key
        self._id = lock_id
        self._lock_type = lock_type
        self._expire = expire
    
    @property
    def lock_val(self) -> Tuple[str, str, str]:
        return self._conn.get(self._key).decode().spilt("+")
    
    @property
    def is_my_lock(self):
        if not self._conn.exists(self._key):
            raise ValueError("the lock is not exist")
        _id, _, _ = self.lock_val
        return self._id == _id
    
    def acquire(self, timeout: Optional[int]=None) -> bool:
        '''加锁操作
        args:
            timeout 为None表示不阻塞，存在值时表示阻塞的毫秒值
        '''
        if not isinstance(timeout, None, int):
            raise ValueError("time_out need None or int type")
        if timeout and timeout < 0:
            raise ValueError("time_out is muat large zero")
        init_lock_val = f"{self._id}+{self._lock_type}+{0}"
        busy = not self._conn.set(self._key, init_lock_val, nx=True, ex=self._expire) # 如果加锁成功那么 busy就为False，否则为True，加锁失败
        if busy:
            # 如果是你自己的锁，再次加锁时，会将times+1
            # 如果这里被执行，说明已经存在锁
            _id, lock_type, times = self.lock_val
            if self.is_my_lock:
                times = int(times) + 1
                self._conn.set(self._key, f"{_id}+{lock_type}+{times}", ex=self._expire)
                return True
            # 如果都是读锁，那么直接返回，不需要获得锁
            if self._lock_type == lock_type == 'r':
                return True
        start_time = time.time()
        while busy:
            busy = not self._conn.set(self._key, init_lock_val, nx=True, ex=self._expire)
            if busy:
                if timeout is None:
                    return False
                if time.time() - timeout > start_time: # 超时退出
                    return False
        return True
    
    def release(self):
        '''释放锁，考虑如何支持重入释放
        如果锁存在、并且时自己的锁，那么就将锁的times减一，直达times==0时直接删除key
        '''
        if not self.is_my_lock:
            raise ValueError("This lock is not your")
        _id, lock_type, times = self.lock_val
        times = int(times) - 1
        if times == 0:
            self._conn.delete(self._key)
            return
        self._conn.set(self._key, f"{_id}+{lock_type}+{times}", ex=self._expire)
