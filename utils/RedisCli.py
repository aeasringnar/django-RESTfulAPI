import time
import redis
import logging
import pickle
from django.conf import settings
from utils.Singleton import Singleton
from typing import Optional, Any, List, Dict, Tuple


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
    
    def __init__(self, key: str) -> None:
        '''初始化操作类，接收一个key作为哈希表的键'''
        self._conn = RedisCli().coon
        self._data_key = key
    
    def __repr__(self) -> str:
        to_dict = {key: self.get(key) for key in map(lambda x: x.decode(), self._conn.hkeys(self._data_key))} if not self.is_empty else {}
        return str(to_dict)

    __str__ = __repr__
    
    @property
    def is_empty(self) -> bool:
        '''检查哈希表是否为空'''
        return not self._conn.exists(self._data_key)
    
    def get(self, key: str, not_exist_val: Any=None):
        '''获取键值，支持设置不存在的默认值，默认为None'''
        val = self._conn.hget(self._data_key, key)
        if val is not None:
            return pickle.loads(val)
        return not_exist_val
    
    def setdefault(self, key: str, data: Any) -> Any:
        '''设置键值'''
        data = pickle.dumps(data)
        self._conn.hset(self._data_key, key, data)
        return data
    
    def __len__(self) -> int:
        '''获取哈希表的长度'''
        if self.is_empty:
            return 0
        return self._conn.hlen(self._data_key)
    
    def __getitem__(self, key: str) -> Any:
        if self.get(key) is None:
            raise KeyError(f"this key {key} is notfound")
        return self.get(key)
    
    def __setitem__(self, key: str, data: Any) -> Any:
        return self.setdefault(key, data)
    
    def __delitem__(self, key: str) -> bool:
        return bool(self._conn.hdel(self._data_key, key))
    
    def values(self) -> List[Any]:
        res_ls = []
        for key in self.keys():
            res_ls.append(self.get(key))
        return res_ls
    
    def __iter__(self):
        return iter(list(map(lambda x: x.decode(), self._conn.hkeys(self._data_key))))
    
    def keys(self) -> List[str]:
        return list(map(lambda x: x.decode(), self._conn.hkeys(self._data_key)))
        

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