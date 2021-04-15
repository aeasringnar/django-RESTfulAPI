import os
import sys
import yaml
from django.conf import settings


class ReadYaml():
    def __init__(self, filename):
        self.filepath = os.path.join(settings.CONF_FILE_PATH, filename)

    def get_data(self):
        with open(self.filepath, "r", encoding="utf-8")as f:
            return yaml.load(f, Loader=yaml.FullLoader)


if __name__ == '__main__':
    data = ReadYaml("data.yaml").get_data()
    print(data.get('pro').get('admin_chengdui'))