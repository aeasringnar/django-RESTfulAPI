import time
import logging
from datetime import datetime, timedelta
from typing import *


class MyDateTime:
    
    @staticmethod
    def timestamp_str(timestamp: int, format: str="%Y-%m-%d %H:%M:%S") -> str:
        '''将 毫秒 时间戳转为字符串的时间，可以指定格式化字符串'''
        try:
            if not isinstance(timestamp, int):
                raise ValueError("The timestamp need int type.")
            if len(str(timestamp)) != 13:
                raise ValueError("The timestamp length need 13.")
            timestamp /= 1000
            return time.strftime(format, time.localtime(timestamp))
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def str_timestamp(time_str: str, format: str) -> int:
        '''将时间字符串转为 毫秒 时间戳，传入的时间字符串要和格式化字符串相匹配
        注：支持毫秒的时间戳转换，例如 2022-01-01 00:10:10.567 对应的时间格式化字符串为 %Y-%m-%d %H:%M:%S.%f
        '''
        try:
            # int(time.mktime(time.strptime(time_str, format)) * 1000) # 废弃，因为无法处理带毫秒的时间字符串
            return (datetime.strptime(time_str, format)).timestamp() * 1000
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def timestamp_datetime(timestamp: int) -> datetime:
        '''将 毫秒 时间戳转为datetime对象'''
        try:
            timestamp /= 1000
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def datetime_timestamp(date_time: datetime) -> int:
        '''将datetime对象转为 毫秒 时间戳'''
        try:
            return int(date_time.timestamp() * 1000)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def str_datetime(time_str: str, format: str) -> datetime:
        '''将时间字符串转为datetime对象'''
        try:
            return datetime.strptime(time_str, format)
        except Exception as e:
            logging.error(str(e))
            raise e
    
    @staticmethod
    def datetime_str(date_time: datetime, format: str) -> str:
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