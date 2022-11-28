from redis_lock import Lock
from utils.RedisCli import RedisCli


def get_redis_lock(key):
    return Lock(RedisCli().coon, key)