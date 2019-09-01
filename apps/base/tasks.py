from __future__ import absolute_import, unicode_literals
from celery import shared_task
from base_django_api.celery import app
import time


@app.task
def add(x, y):
    return x + y

@app.task
def say():
    return '你好'

@shared_task
def mul(x, y):
    print('发生耗时操作...')
    time.sleep(10)
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)