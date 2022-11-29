from redis import StrictRedis
from datetime import datetime
from enum import Enum
'''
新版的分布式可充入读写锁
实现原理：
1、基本的分布式锁原理，通过设置redis的key nx 即如果key存在则创建，否则返回none，创建锁时增加过期时间参数，默认30秒
2、可以同个key的值加上锁类型，读锁或写锁 以及锁id(防止锁被别人释放) 加上加锁次数 目的是支持可重入的锁，当加锁次数为0时，释放锁
3、在加锁时增加timeout参数，毫秒值，如果有值那么表示加锁时，如果锁被人锁着，那么就进行重试等待 值表示等待的时间，为None时表示不阻塞，有锁时直接返回加锁失败。
4、使用上下文管理器，进入时加锁，离开时释放锁，
'''


class RedisLock:
    
    def __init__(self, redis_conn: StrictRedis, lock_id: str, lock_type: str='w', expire: int=30) -> None:
        '''锁的初始化
        args:
            redis_conn Redis连接对象
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
        self._conn = redis_conn