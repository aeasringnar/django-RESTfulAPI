import time
import logging
from datetime import datetime, timedelta


class MyDateTime:
    '''自定义的时间处理类
    定义时间戳为整型的，微妙时间戳13位，微妙时间戳当前时间到百年之内位16位，当时间更大，会出现16位以上。
    本例时间戳定义为微妙级别，更加精确。
    秒时间戳：10位
    1秒 = 10**3毫秒 = 10**6微秒 = 10**纳秒
    注意：unix时间戳是自1970-01-01 08:00:00以来经过的秒数。
        Unix时间传统用一个32位的整数进行存储。这会导致“2038年”问题，当这个32位的unix时间戳不够用，产生溢出，使用这个时间的遗留系统就麻烦了。
    '''
    
    @staticmethod
    def _validate_timestamp_for_ns(timestamp: int):
        '''验证传入的微妙时间戳是否合法'''
        if not isinstance(timestamp, int):
            raise ValueError("The timestamp need int type.")
        if len(str(timestamp)) != 16:
            raise ValueError("The timestamp is invalid.")
    
    @staticmethod
    def _validate_time_str(time_str: str, format: str="%Y-%m-%d %H:%M:%S"):
        '''验证传入的时间字符串是否合法'''
        if not isinstance(time_str, str):
            raise ValueError("The timestamp need str type.")
        try:
            datetime.strptime(time_str, format)
        except Exception:
            raise ValueError("The time_str is invalid.")
    
    @staticmethod
    def _validate_datetime_obj(date_time: datetime):
        '''验证传入的时间对象是否合法'''
        if not isinstance(date_time, datetime):
            raise ValueError("The timestamp need datetime type.")
    
    @staticmethod
    def _validate_timetuple(timetuple: time.struct_time):
        '''验证传入的时间元组是否合法'''
        if not isinstance(timetuple, time.struct_time):
            raise ValueError("The timestamp need struct_time type.")
    
    @staticmethod
    def timestamp_to_str(timestamp: int, format: str="%Y-%m-%d %H:%M:%S") -> str:
        '''将 微妙 时间戳转为字符串的时间，可以指定格式化字符串'''
        try:
            MyDateTime._validate_timestamp_for_ns(timestamp)
            timestamp /= 1e6
            # time.strftime(format, time.localtime(timestamp)) # 废弃，因为精度不高，不支持微妙的精度
            return datetime.fromtimestamp(timestamp).strftime(format)
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def timestamp_to_datetime(timestamp: int) -> datetime:
        '''将 微妙 时间戳转为datetime对象'''
        try:
            MyDateTime._validate_timestamp_for_ns(timestamp)
            timestamp /= 1e6
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def str_to_timestamp(time_str: str, format: str="%Y-%m-%d %H:%M:%S") -> int:
        '''将时间字符串转为 微妙 时间戳，传入的时间字符串要和格式化字符串相匹配
        注：支持微妙的时间戳转换，例如 2022-01-01 00:10:10.567 对应的时间格式化字符串为 %Y-%m-%d %H:%M:%S.%f
        '''
        try:
            # int(time.mktime(time.strptime(time_str, format)) * 1000) # 废弃，因为无法处理带微妙的时间字符串
            MyDateTime._validate_time_str(time_str, format)
            return int(datetime.strptime(time_str, format).timestamp() * 1e6)
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def str_to_datetime(time_str: str, format: str="%Y-%m-%d %H:%M:%S") -> datetime:
        '''将时间字符串转为datetime对象'''
        try:
            MyDateTime._validate_time_str(time_str, format)
            return datetime.strptime(time_str, format)
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def datetime_to_timestamp(date_time: datetime) -> int:
        '''将datetime对象转为 微妙 时间戳'''
        try:
            MyDateTime._validate_datetime_obj(date_time)
            return int(date_time.timestamp() * 1e6)
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def datetime_to_str(date_time: datetime, format: str="%Y-%m-%d %H:%M:%S") -> str:
        '''将datetime对象转为时间字符串'''
        try:
            MyDateTime._validate_datetime_obj(date_time)
            return datetime.strftime(date_time, format)
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def datetime_to_timetuple(date_time: datetime) -> time.struct_time:
        '''将datetime对象转为时间元组'''
        try:
            MyDateTime._validate_datetime_obj(date_time)
            return date_time.timetuple()
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def timetuple_to_datetime(timetuple: time.struct_time) -> datetime:
        '''将时间元组转为datetime对象'''
        try:
            MyDateTime._validate_timetuple(timetuple)
            return datetime.fromtimestamp(time.mktime(timetuple))
        except Exception as e:
            logging.error(str(e))
            raise e

    @staticmethod
    def timestr_to_newtimestr(time_str: str, old_format: str, new_format: str) -> str:
        '''将一个时间字符串格式转为新的时间字符串格式'''
        try:
            MyDateTime._validate_time_str(time_str, old_format)
            return datetime.strptime(time_str, old_format).strftime(new_format)
        except Exception as e:
            logging.error(str(e))
            raise e


if __name__ == "__main__":
    t = int(time.time() * 1e6)
    # print(MyDateTime.timestamp_to_str(1662886461423443))
    # print(MyDateTime.timestamp_to_str(t, "%Y-%m-%d %H:%M:%S"))
    # print(MyDateTime.timestamp_to_datetime(t))
    
    # print(MyDateTime.str_to_timestamp("2022-09-10 10:10:10.324567", "%Y-%m-%d %H:%M:%S.%f"))
    # print(MyDateTime.str_to_timestamp("2022-09-10 10:10:10", "%Y-%m-%d %H:%M:%S"))
    # print(MyDateTime.timestamp_to_str(MyDateTime.str_to_timestamp("2022-09-10 10:10:10", "%Y-%m-%d %H:%M:%S")))
    # print(MyDateTime.str_to_datetime("2020-09-10 10:10:10"))

    # print(MyDateTime.datetime_to_timestamp(datetime.now()))
    # print(MyDateTime.datetime_to_str(datetime.now()))
    # print(MyDateTime.datetime_to_timetuple(datetime.now()))
    
    print(MyDateTime.timetuple_to_datetime(time.localtime()))
    print(MyDateTime.timestr_to_newtimestr("2022-09-10 10:10:10", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"))
    print(MyDateTime.timestr_to_newtimestr("2022-09-10 10:10:10", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"))