from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from os import system, makedirs
from pathlib import Path
import json
import logging
import sys


class Command(BaseCommand):
    help = "Command for generate template code."
    now_dir = Path(__file__).resolve().parent.parent.parent
    generate_template_dir = Path.joinpath(now_dir, 'generate_template')
    base_str_path_dic = {
        'serializer': Path.joinpath(generate_template_dir, 'serializer.txt'),
        'url': Path.joinpath(generate_template_dir, 'url.txt'),
        'view': Path.joinpath(generate_template_dir, 'view.txt')
    }
    
    def get_base_str(self, str_type: str) -> str:
        with open(self.base_str_path_dic[str_type], 'r') as f:
            return f.read()
    
    def generate_item_code(self, app_path: str, file_name: str, content: str) -> bool:
        '''生成文件的方法'''
        with open(Path.joinpath(app_path, file_name), 'a') as f:
            f.write(content)
        return True

    def handle(self, *args, **options):
        json_path = Path.joinpath(settings.CONFIG_DIR, 'generateCode.json')
        with open(json_path, 'r') as f:
            generate_data = json.loads(f.read())
        for data in generate_data:
            app_name = data['app_name']
            app_path = Path(Path.joinpath(settings.MY_APPS_DIR, app_name))
            if not app_path.exists():
                raise CommandError("This app(%s) is not exists." % app_name)
            # 开启生成代码的流程
            print('即将开始生成代码的App名称：{}'.format(app_name))
            models = data.get('models')
            w_serializer = []
            w_view = []
            w_url_router = []
            viewsets = []
            w_url_import, base_url_router = self.get_base_str('url').split('\n')
            for model_item in models:
                model_name = model_item.get('model_name')
                verbose = model_item.get('verbose')
                base_ser = self.get_base_str('serializer')
                w_serializer.append(base_ser.format(model_name=model_name, verbose=verbose))
                if model_item.get('searchs'):
                    searchs = ["'{}'".format(item) for item in model_item.get('searchs')]
                    search_str = ", ".join(searchs) if len(searchs) > 1 else "%s, " % searchs[0]
                    search_str = '''\n    search_fields = (%s)''' % search_str
                else:
                    search_str = ''
                if model_item.get('filters'):
                    filters = ["'{}'".format(item) for item in model_item.get('filters')]
                    filter_str = ", ".join(filters) if len(filters) > 1 else "%s, " % filters[0]
                    filter_str = '''\n    filterset_fields = (%s)''' % filter_str
                else:
                    filter_str = ''
                base_view = self.get_base_str('view')
                w_view.append(base_view.format(verbose=verbose, model_name=model_name, search_str=search_str, filter_str=filter_str))
                viewsets.append("{}Viewset".format(model_name))
                lower = "{}{}".format(model_name[0].lower(), model_name[1:])
                w_url_router.append(base_url_router.format(lower=lower, model_name=model_name, verbose=verbose))
            
            w_url_import = w_url_import.format(app_name=app_name, viewsets=', '.join(viewsets))
            w_w_url_router = "{}\nurlpatterns = [\n    path('', include(router.urls)),\n]\n".format('\n'.join(w_url_router))
            self.generate_item_code(app_path, 'serializers.py', '\n\n\n'.join(w_serializer))
            print("App：{} 的序列化器文件生成完毕。".format(app_name))
            self.generate_item_code(app_path, 'views.py', '\n\n\n'.join(w_view))
            print("App：{} 的视图文件生成完毕。".format(app_name))
            self.generate_item_code(app_path, 'urls.py', f'\n{w_url_import}\n')
            self.generate_item_code(app_path, 'urls.py', '\n\nrouter = DefaultRouter()\n')
            self.generate_item_code(app_path, 'urls.py', w_w_url_router)
            print("App：{} 的路由文件生成完毕。".format(app_name))