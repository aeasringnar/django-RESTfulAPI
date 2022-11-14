import yaml
from pathlib import Path
from django.conf import settings


class ReadYaml:
    '''用于读取yaml文件的类'''
    
    def __init__(self, file_name: str, is_path: bool=False) -> None:
        self.filepath = file_name if is_path else Path.joinpath(settings.CONFIG_DIR, file_name)

    def get_data(self):
        with open(self.filepath, "r", encoding="utf-8")as f:
            return yaml.load(f, Loader=yaml.FullLoader)


if __name__ == '__main__':
    data = ReadYaml("data.yaml").get_data()
    print(data.get('pro').get('admin_chengdui'))