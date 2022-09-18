from django.apps import AppConfig


class PublicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.public'

    def ready(self):
        import apps.public.signals