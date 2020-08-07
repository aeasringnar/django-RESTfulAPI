import os
import logging
from django.conf import settings
log_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), 'web.log')

# 创建 logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# logger.propagate = 0

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.DEBUG)
# 创建一个输出到文件的 handler
fileHandler = logging.FileHandler(log_path, mode='w')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.INFO)
if settings.DEBUG:
    fileHandler.setLevel(logging.DEBUG)
else:
    fileHandler.setLevel(logging.INFO)

if settings.DEBUG:
    logger.addHandler(consoleHandler) 
logger.addHandler(fileHandler)