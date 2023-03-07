import math
import hmac
import time
import random
import hashlib
from uuid import uuid1
from datetime import datetime
from typing import Union
'''
Python中UUID的区别
uuid1(node=None, clock_seq=None) 根据主机 ID、序列号和当前时间生成一个 UUID。 如果没有给出 node，则使用 getnode() 来获取硬件地址。
        如果给出了 clock_seq，它将被用作序列号；否则将选择一个随机的 14 比特位序列号。
uuid3(namespace, name) 根据命名空间标识符（这是一个UUID）和名称（这是一个字符串）的MD5哈希值，生成一个UUID。
uuid4() 生成一个随机的UUID。注意：可能会重复。
uuid5(namespace, name) 根据命名空间标识符（这是一个UUID）和名称（这是一个字符串）的SHA-1哈希值生成一个UUID。
'''


class NormalObj:
    '''一个统一的类，目的是将分散的一些通用方法进行归集'''

    @staticmethod
    def to_sha256(payload: str) -> str:
        '''生成哈希256的散列值，返回长度为64位的字符串，其值为64位的16进制数组成'''
        h = hashlib.sha256()
        h.update(payload.encode(encoding='utf8'))
        return h.hexdigest()

    @staticmethod
    def create_random_code(length: int=6, abc: bool=True) -> str:
        '''生成随机验证码'''
        base_str = '0123456789qwerrtyuioplkjhgfdsazxcvbnm' if abc else '01234567890123456789'
        # return ''.join([random.choice(base_str) for _ in range(length)])
        return ''.join(random.choices(list(base_str), k=length))

    @staticmethod
    def create_unique_order_no() -> str:
        now_date_time_str = str(
            datetime.now().strftime('%Y%m%d%H%M%S%f'))
        base_str = '01234567890123456789'
        random_num = ''.join(random.sample(base_str, 6))
        random_num_two = ''.join(random.sample(base_str, 6))
        return ''.join(now_date_time_str, random_num, random_num_two)
    
    @staticmethod
    def uuid1_int() -> int:
        return int(uuid1())

    @staticmethod
    def get_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        '''计算两经纬度之间的距离 返回距离单位为公里'''
        radLat1 = (lat1 * math.pi / 180.0)
        radLat2 = (lat2 * math.pi / 180.0)
        a = radLat1 - radLat2
        b = (lng1 * math.pi / 180.0) - (lng2 * math.pi / 180.0)
        s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(math.sin(b/2), 2)))
        s = s * 6378.137
        return s
    
    @staticmethod
    def check_number_divisible(dividend: Union[float, int], divisor: Union[float, int]):
        '''检查被除数是否能被除数除尽'''
        mod = dividend % divisor
        mod_set = set()
        while mod != 0 and mod not in mod_set:
            mod_set.add(mod)
            if mod * 10 > divisor:
                mod = (mod * 10) % divisor
            else:
                mod = (mod * 10 ** len(str(divisor))) % divisor
        if mod == 0:
            return True
        return False


if __name__ == "__main__":
    print(NormalObj.check_number_divisible(4950, 156))