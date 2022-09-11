import time
import logging
from datetime import datetime, timedelta
from typing import *


class MyDateTime:
    '''自定义的时间处理类
    定义时间戳为整型的，纳秒时间戳13位，纳秒时间戳当前时间到百年之内位16位，当时间更大，会出现16位以上。
    本例时间戳定义为纳秒级别，更加精确。
    '''
    
    @staticmethod
    def timestamp_str(timestamp: int, format: str="%Y-%m-%d %H:%M:%S") -> str:
        '''将 纳秒 时间戳转为字符串的时间，可以指定格式化字符串'''
        try:
            if not isinstance(timestamp, int):
                raise ValueError("The timestamp need int type.")
            timestamp /= 1e6
            # time.strftime(format, time.localtime(timestamp)) # 废弃，因为精度不高，不支持纳秒的精度
            return datetime.fromtimestamp(timestamp).strftime(format)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def str_timestamp(time_str: str, format: str="%Y-%m-%d %H:%M:%S") -> int:
        '''将时间字符串转为 纳秒 时间戳，传入的时间字符串要和格式化字符串相匹配
        注：支持纳秒的时间戳转换，例如 2022-01-01 00:10:10.567 对应的时间格式化字符串为 %Y-%m-%d %H:%M:%S.%f
        '''
        try:
            # int(time.mktime(time.strptime(time_str, format)) * 1000) # 废弃，因为无法处理带纳秒的时间字符串
            return int(datetime.strptime(time_str, format).timestamp() * 1e6)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def timestamp_datetime(timestamp: int) -> datetime:
        '''将 纳秒 时间戳转为datetime对象'''
        try:
            timestamp /= 1e6
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def datetime_timestamp(date_time: datetime) -> int:
        '''将datetime对象转为 纳秒 时间戳'''
        try:
            return int(date_time.timestamp() * 1e6)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def str_datetime(time_str: str, format: str="%Y-%m-%d %H:%M:%S") -> datetime:
        '''将时间字符串转为datetime对象'''
        try:
            return datetime.strptime(time_str, format)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def datetime_str(date_time: datetime, format: str="%Y-%m-%d %H:%M:%S") -> str:
        '''将datetime对象转为时间字符串'''
        try:
            return datetime.strftime(date_time, format)
        except Exception as e:
            logging.error(str(e))
            raise e
        
    @staticmethod
    def timetuple_datetime(timetuple: time.struct_time) -> datetime:
        '''将时间元组转为datetime对象'''
        try:
            return datetime.fromtimestamp(time.mktime(timetuple))
        except Exception as e:
            logging.error(str(e))
            raise e
        
    @staticmethod
    def datetime_timetuple(date_time: datetime) -> time.struct_time:
        '''将datetime对象转为时间元组'''
        try:
            return date_time.timetuple()
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def timestr_newtimestr(time_str: str, old_format: str, new_format: str) -> str:
        '''将一个时间字符串格式转为新的时间字符串格式'''
        try:
            return datetime.strptime(time_str, old_format).strftime(new_format)
        except Exception as e:
            logging.error(str(e))
            raise e


if __name__ == "__main__":
    t = int(time.time() * 1e6)
    # print(MyDateTime.timestamp_str(t, "%Y-%m-%d %H:%M:%S.%f"))
    # print(MyDateTime.timestamp_str(t, "%Y-%m-%d %H:%M:%S"))
    # print(MyDateTime.str_timestamp("2022-09-10 10:10:10.324567", "%Y-%m-%d %H:%M:%S.%f"))
    print(MyDateTime.str_timestamp("2020-09-10 10:10:10"))
    print(MyDateTime.str_timestamp("2022-09-10 10:10:10"))
    print(MyDateTime.str_timestamp("2027-09-10 10:10:10"))
    print(MyDateTime.str_timestamp("2032-09-10 10:10:10"))
    # print(MyDateTime.timestamp_datetime(t))
    # print(MyDateTime.datetime_timestamp(datetime.now()))
    # print(MyDateTime.str_datetime("2022-09-10 10:10:10.324567", "%Y-%m-%d %H:%M:%S.%f"))
    # print(MyDateTime.str_datetime("2022-09-10 10:10:10"))
    # print(MyDateTime.datetime_str(datetime.now(), "%Y-%m-%dT%H:%M:%S.%f"))
    # print(MyDateTime.datetime_str(datetime.now(), "%Y-%m-%dT%H:%M:%S.%f"))
    # print(MyDateTime.datetime_str(datetime.now(), "%Y-%m-%dT%H:%M:%S"))
    # print(MyDateTime.timetuple_datetime(time.localtime()))
    # print(MyDateTime.datetime_timetuple(datetime.now()))
    # print(MyDateTime.timestr_newtimestr("2022-09-10 10:10:10", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"))
    # print(MyDateTime.timestr_newtimestr("2022-09-10 10:10:10", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"))