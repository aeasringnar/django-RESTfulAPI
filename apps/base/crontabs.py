from .models import ConfDict
import datetime

# 定时任务 
def confdict_handle():
    try:
        loca_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('本地时间：'+str(loca_time))
    except Exception as e:
        print('发生错误，错误信息为：', e)