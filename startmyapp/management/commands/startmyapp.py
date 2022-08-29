from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from os import system, makedirs
from pathlib import Path


class Command(BaseCommand):
    help = "Command for creating a custom app."

    def add_arguments(self, parser):
        '''为命令添加一个参数，就是要创建app的名称，用来调用内置的startapp的必传参数。'''
        parser.add_argument('app_name')

    def handle(self, *args, **options):
        '''实际是业务逻辑，根据自己的需要，变更原来的创建新的app的逻辑。'''
        app_name = options['app_name']
        app_path = Path(Path.joinpath(settings.MY_APPS_DIR, app_name))
        if app_path.exists():
            raise CommandError("This app(%s) is exists." % app_name)
        makedirs(app_path)
        cmd = "python manage.py startapp --template={} {} {}".format(settings.MY_APP_TEMPLATE, app_name, app_path)
        # 执行实际的创建app的命令
        system(cmd)