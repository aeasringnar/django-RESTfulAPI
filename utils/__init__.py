import logging.config
from utils.ReadYaml import ReadYaml


# 初始化日志输出
logging.config.dictConfig(ReadYaml('logging.yaml').get_data())