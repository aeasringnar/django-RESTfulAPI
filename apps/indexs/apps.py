from django.apps import AppConfig


class IndexsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.indexs'

    def ready(self):
        import apps.indexs.signals