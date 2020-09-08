from django.apps import AppConfig


class PublicConfig(AppConfig):
    name = 'public'

    # 激活signals
    def ready(self):
        import public.signals
