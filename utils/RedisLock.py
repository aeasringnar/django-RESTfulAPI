import time
import threading
from .RedisCli import RedisCli


class RedisReadWriteLock(object):
    def __init__(self, cache_key, cache_type, time_out=60):
        self.redis = RedisCli()
        self.redis_con = self.redis.coon
        self.cache_key = cache_key
        self.cache_type = cache_type
        self.time_out = time_out

    def get_lock(self, val):
        val = val + ':' + self.cache_type
        while True:
            res = self.redis_con.set(self.cache_key, val, nx=True, ex=self.time_out)
            if res:
                # 表示获得锁成功，跳出循环
                print('写操作获得锁成功' if self.cache_type == 'write' else "读操作获得锁成功")
                break
            else:
                # 此时说明已经存在数据
                # 表示等待锁的过程，但是有一种情况是：如果检测到锁为读锁，来的操作也是读操作，那么不阻塞
                if self.cache_type == 'read':
                    try:
                        check_type = str(self.redis_con.get(self.cache_key).decode()).split(':')[1]
                        if check_type == 'read':
                            print('读操作，无需获得锁，直接读取。')
                            break
                    except:
                        res = self.redis_con.set(self.cache_key, val, nx=True, ex=self.time_out)
                        if res:
                            break
            time.sleep(0.1)

    def del_lock(self, val):
        val = val + ':' + self.cache_type
        old_val = self.redis_con.get(self.cache_key)
        if old_val == val.encode():
            self.redis_con.delete(self.cache_key)


SUMS = 0

def test_lock(name, num, val):
    try:
        if num % 2 == 0:
            lock = RedisReadWriteLock('new_cache_key', 'write')
        else:
            lock = RedisReadWriteLock('new_cache_key', 'read')
        print('%s 开始工作' % name)
        print('%s 准备获取锁并加锁' % name)
        lock.get_lock(val)
        print('%s 得到锁，继续工作' % name)
        global SUMS
        if num % 2 == 0:
            SUMS += 15
            time.sleep(5)
            print('+++++++++++++++++++写操作++++++++++++++++')
        else:
            time.sleep(1)
            print('**********************读操作******************')
        print(SUMS)
    except Exception as e:
        print('发生异常：%s' % str(e))
    finally:
        print('%s 操作完成，准备释放锁'%name)
        lock.del_lock(val)


def test_main():
    start_time = time.time()
    tasks = []
    for num in range(1, 6):
        t = threading.Thread(target=test_lock, args=('任务%d'%num, num, 'lock%d'%num))
        tasks.append(t)
        t.start()
    [item.join() for item in tasks]
    print('总耗时：', time.time() - start_time)

if __name__ == '__main__':
    test_main()