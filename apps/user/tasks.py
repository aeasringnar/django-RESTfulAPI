import os
import sys
import json
import time
import logging
import threading
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction
from django.core.cache import caches
from django.forms.models import model_to_dict
from celery import shared_task
from drfAPI.celery import app


# create your async task here

# @app.task(bind=True)
# def async_task(self, *args, **kwargs):
#     try:
#         pass
#     except Exception as e:
#         logging.error("async task has error {}".fromat(e))
#         logging.exception(e)
#         # 执行失败重试，本例设置3分钟后重试
#         self.retry(countdown=60 * 3, exc=e)