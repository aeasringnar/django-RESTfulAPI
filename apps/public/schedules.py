import os, sys, time, datetime
import threading
import django
base_apth = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(base_apth)
# 将项目路径加入到系统path中，这样在导入模型等模块时就不会报模块找不到了
sys.path.append(base_apth)
os.environ['DJANGO_SETTINGS_MODULE'] ='base_django_api.settings'
django.setup()
from public.models import ConfDict

def confdict_handle():
    while True:
        try:
            loca_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('本地时间：'+str(loca_time))
            time.sleep(10)
        except Exception as e:
            print('发生错误，错误信息为：', e)
            continue


def main():
    '''
    主函数，用于启动所有定时任务，因为当前定时任务是手动实现，因此可以自由发挥
    '''
    try:
        # 启动定时任务，多个任务时，使用多线程
        task1 = threading.Thread(target=confdict_handle)
        task1.start()
    except Exception as e:
        print('发生异常：%s' % str(e))

if __name__ == '__main__':
    main()