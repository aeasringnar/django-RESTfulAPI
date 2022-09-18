from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from os import system, makedirs
from pathlib import Path
import json


class Command(BaseCommand):
    help = "Command for generate template code."

    # def add_arguments(self, parser):
    #     '''为命令添加一个参数，就是要创建app的名称，用来调用内置的startapp的必传参数。'''
    #     parser.add_argument('app_name')
    now_dir = Path.absolute(__file__).parent.parent.parent
    generate_template_dir = Path.joinpath(now_dir, 'generate_template')
    base_str_path_dic = {
        'serializer': Path.joinpath(generate_template_dir, 'serializer.txt'),
        'url': Path.joinpath(generate_template_dir, 'url.txt'),
        'view': Path.joinpath(generate_template_dir, 'view.txt')
    }
    
    def get_base_str(self, str_type: str) -> str:
        with open(self.base_str_path_dic[str_type], 'r') as f:
            return f.read()

    def handle(self, *args, **options):
        json_path = Path.joinpath(settings.CONFIG_DIR, 'generateCode.json')
        generate_data = json.load(json_path)
        for data in generate_data:
            app_name = data['app_name']
            app_path = Path(Path.joinpath(settings.MY_APPS_DIR, app_name))
            if not app_path.exists():
                raise CommandError("This app(%s) is not exists." % app_name)
            # 开启生成代码的流程
            print('app：', data)
            models = data.get('models')
            print('所有模型：', models)
            w_serializer = []
            base_ser = self.get_base_str('serializer')
            for model_item in models:
                model_name = model_item.get('model_name')
                verbose = model_item.get('verbose')
                searchs = model_item.get('searchs')
                filters = model_item.get('filters')
                w_serializer.append(base_ser.format(model_name=model_name, verbose=verbose))
            with open(app_path, 'a') as f:
                f.write('\n\n'.join(w_serializer))