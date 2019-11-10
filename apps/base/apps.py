from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'base'

    # 激活signals
    def ready(self):
        import base.signals
