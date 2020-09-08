from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms
from django.conf import settings
# 定时任务需要的包
# from celery.schedules import crontab
# from datetime import timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_django_api.settings')

'''
# redis做MQ配置
app = Celery('website', backend='redis', broker='redis://localhost')
# rabbitmq做MQ配置
app = Celery('website', backend='amqp', broker='amqp://admin:admin@localhost')
'''
app = Celery('base_django_api')

# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('django.conf:settings')

# app.autodiscover_tasks(lambda :settings.INSTALLED_APPS)
app.autodiscover_tasks()

platforms.C_FORCE_ROOT = True

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# 测试的定时任务 定时任务 使用crontab较好
# app.conf.update(
#     CELERYBEAT_SCHEDULE = {
#         'mul-task': {
#             'task': 'public.tasks.mul',
#             'schedule':  timedelta(seconds=30),
#             'args': (5, 6)
#         }
#     }
# )