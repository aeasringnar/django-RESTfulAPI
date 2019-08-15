from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_django_api.settings')

# app = Celery('base_django_api', backend='redis', broker='redis://localhost')
app = Celery('base_django_api')

# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('django.conf:settings')

# app.autodiscover_tasks(lambda :settings.INSTALLED_APPS)
app.autodiscover_tasks()

platforms.C_FORCE_ROOT = True

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))