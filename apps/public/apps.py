from django.apps import AppConfig


class PublicConfig(AppConfig):
    name = 'apps.public' # todo 修改app名称，使应用可以在apps目录中存在，并且可以正常的导入到settings

    # 激活signals
    def ready(self):
        import apps.public.signals
