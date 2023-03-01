import time
import redis
import logging
import pickle
from django.conf import settings
from utils.Singleton import Singleton
from typing import Optional, Any, List, Dict, Tuple
from uuid import uuid1


class RedisCli(Singleton):
    
    def __init__(self) -> None:
        '''初始化'''
        self._connect_url = settings.CACHES['redis_cli']['LOCATION'] # settings.CACHES['redis_cli']['LOCATION']
        self.current_db = int(self._connect_url[-1])
        self.coon = redis.Redis(connection_pool=redis.ConnectionPool().from_url(self._connect_url))
    
    def key_exists(self, key: str) -> bool:
        '''判断键是否存在'''
        return bool(self.coon.exists(key))
    
    def select_db(self, db: int) -> int:
        '''切换Redis数据库'''
        self.coon.select(db)
        self.current_db = db
        return db


class RedisHash(object):
    '''构建操作哈希表的类，使哈希表可以想字典一样使用'''
    
    def __init__(self, key: str=None) -> None:
        '''初始化操作类，接收一个key作为哈希表的键
        args:
            key Redis中存储数据使用的key，给这个参数的目的是为了方便重复操作哈希表，如果为None，说明作为纯字典使用，一旦实例被销毁，Redis中的数据也将销毁
            destory_cache
        '''
        self._conn = RedisCli().coon
        self._data_key = key if not key is None else str(int(uuid1()))
        self._destory_cache = True if key is None else False
    
    def __repr__(self) -> str:
        to_dict = {key: self.get(key) for key in map(lambda x: x.decode(), self._conn.hkeys(self._data_key))} if not self.is_empty else {}
        return str(to_dict)

    __str__ = __repr__
    
    @property
    def id(self):
        '''返回哈希表的key，也作为实例的id'''
        return self._data_key
    
    @property
    def is_empty(self) -> bool:
        '''检查哈希表是否为空'''
        return not self._conn.exists(self._data_key)
    
    def get(self, key: str, not_exist_val: Any=None) -> Any:
        '''获取键值，支持设置不存在的默认值，默认为None'''
        val = self._conn.hget(self._data_key, key)
        if val is not None:
            return pickle.loads(val)
        return not_exist_val
    
    def setdefault(self, key: str, data: Any=None) -> Any:
        '''设置键值'''
        self._conn.hset(self._data_key, key, pickle.dumps(data))
        return data
    
    def __del__(self):
        '''如果是一次性的，对象被销毁时，清除Redis中的哈希表'''
        if self._destory_cache:
            self._conn.delete(self._data_key)
    
    def __len__(self) -> int:
        '''获取哈希表的长度'''
        if self.is_empty:
            return 0
        return self._conn.hlen(self._data_key)

    def _check_key(self, key:str) -> None:
        if key not in self:
            raise KeyError(f"this key {key} is notfound")
    
    def __getitem__(self, key: str) -> Any:
        '''通过 d['key'] 来获取值'''
        self._check_key(key)
        return self.get(key)
    
    def __setitem__(self, key: str, data: Any) -> Any:
        '''通过 d['key'] = val 来设置值'''
        return self.setdefault(key, data)
    
    def __delitem__(self, key: str) -> bool:
        '''通过 del d['key'] 来删除值'''
        self._check_key(key)
        return bool(self._conn.hdel(self._data_key, key))
    
    def values(self) -> List[Any]:
        '''返回哈希表的所有值组成的列表'''
        res_ls = []
        for key in self.keys():
            res_ls.append(self.get(key))
        return res_ls
    
    def __iter__(self):
        '''使这个类的实例支持迭代，可以在for循环中像字典一样被使用'''
        return iter(self.keys())
    
    def keys(self) -> List[str]:
        '''返回哈希表的所有key组成的列表'''
        return list(map(lambda x: x.decode(), self._conn.hkeys(self._data_key)))
    
    def pop(self, key: str, not_exist_val: Any=None) -> Any:
        '''移除字典中指定的键'''
        if key not in self:
            return not_exist_val
        val = self.get(key)
        del self[key]
        return val
    
    def clear(self) -> None:
        '''清空这个字典'''
        self._conn.delete(self._data_key)
        

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