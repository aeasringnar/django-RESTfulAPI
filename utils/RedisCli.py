import redis
import logging
import time
from django.conf import settings
from .Singleton import Singleton





class RedisCli(Singleton):
    
    def __init__(self):
        '''初始化'''
        self.connect_url = settings.CACHES['redis_cli']['LOCATION'] # settings.CACHES['redis_cli']['LOCATION']
        self.current_db = int(self.connect_url[-1])
        self.pool = redis.ConnectionPool().from_url(self.connect_url)
        self.coon = redis.Redis(connection_pool=self.pool)
    
    def key_exists(self, key):
        '''判断键是否存在'''
        return bool(self.coon.exists(key))
    
    def select_db(self, db):
        '''切换Redis数据库'''
        self.coon.select(db)
        self.current_db = db
        return db


class RedisHash(object):
    
    def __init__(self, hash_key):
        '''初始化，需要传入哈希表的key'''
        self.redis = RedisCli()
        self.coon = self.redis.coon
        self.hash_key = hash_key
        self.has_key = self.redis.key_exists(self.hash_key)
        if not self.has_key:
            logging.warning(f'key: {self.hash_key} not found')
        if self.has_key and self.coon.type(self.hash_key).decode() != 'hash':
            raise KeyError(f'key: {self.hash_key} is not hash type')
        
    def get_val(self, key):
        '''获取指定的键值
        args：
            key str：目标键
        returns：
            any/None：返回存储的值或None
        '''
        val = self.coon.hget(self.hash_key, key)
        if val:
            return val.decode()
        return val
    
    def set_val(self, key, val):
        '''设置新的键值对，如果已经存在，就返回来的键值，不会覆盖
        args：
            key str：目标键
            val any：存储的值
        returns：
            any：返回存储的值
        '''
        if not self.has_key:
            self.coon.hset(self.hash_key, key, val)
            return val
        if self.get_val(key):
            return self.get_val(key)
        self.coon.hset(self.hash_key, key, val)
        return val
    
    def del_val(self, *key):
        '''删除指定的键值对
        args：
            *key str：目标键，可以传多个键
        returns：
            int：返回删除成功的键值对数量
        '''
        return self.coon.hdel(self.hash_key, *key)
    
    @property
    def length(self):
        '''得到当前哈希表的长度'''
        if not self.has_key:
            return 0
        return self.coon.hlen(self.hash_key)
        

if __name__ == '__main__':
    # redis_cli = RedisHash('new')
    # print(redis_cli.get_val('a'))
    # print(redis_cli.get_val('b'))
    
    # redis_cli = RedisHash('ns')
    # print(redis_cli.set_val('x', 123))
    # print(redis_cli.set_val('y', 345))
    # print(redis_cli.set_val('z', '567'))
    # print(redis_cli.del_val('x'))
    # print(redis_cli.length)
    
    r1 = RedisCli()
    r2 = RedisCli()
    r3 = RedisCli()
    r4 = RedisCli()
    print(id(r1), id(r2), id(r3), id(r4))
    print(id(r1.pool), id(r2.pool), id(r3.pool), id(r4.pool))
    print(id(r1.coon), id(r2.coon), id(r3.coon), id(r4.coon))
    while 1:
        r1.coon.ping()
        r2.coon.ping()
        r3.coon.ping()
        time.sleep(1)