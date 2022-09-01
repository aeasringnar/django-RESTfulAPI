from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# line database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'anymeta',
        'USER': 'debian-sys-maint',
        'PASSWORD': 'ztV6GraofMkqmDL7',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",  # 去除强制外键约束
            'charset': 'utf8mb4',
            'sql_mode': 'traditional'
        },
        'CONN_MAX_AGE': 100 # 持久连接 定义了一个MySQL链接最大寿命，是一个秒数，表明一个连接的存活时间。
    }
}
'''
sql_mode
ANSI模式：宽松模式，对插入数据进行校验，如果不符合定义类型或长度，对数据类型调整或截断保存，报warning警告。
TRADITIONAL 模式：严格模式，当向mysql数据库插入数据时，进行数据的严格校验，保证错误数据不能插入，报error错误。用于事物时，会进行事物的回滚。
STRICT_TRANS_TABLES模式：严格模式，进行数据的严格校验，错误数据不能插入，报error错误。
'''


# 日志配置
LOGGING = {
    'version': 1,  # 指明dictConnfig的版本
    'disable_existing_loggers': False,  # 表示是否禁用所有的已经存在的日志配置
    'formatters': {  # 格式器
        'verbose': {  # 详细
            'format': '[%(levelname)s] %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'standard': {  # 标准
            'format': '[%(asctime)s] %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        },
        "debug": { # 调试
            "format": "[%(asctime)s] [%(process)d:%(thread)d] %(filename)s[line:%(lineno)d] (%(name)s)[%(levelname)s] %(message)s",
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'standard'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "debug",
            "level": "DEBUG",
            "encoding": "utf8",
            "filename": "./logs/debug.log",
            "mode": "w"
        },
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": "INFO",
            "encoding": "utf8",
            "filename": "./logs/info.log",
            "mode": "w"
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "debug",
            "level": "ERROR",
            "encoding": "utf8",
            "filename": "./logs/error.log",
            "mode": "w"
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        },
        # 用于关闭django默认的request日志 必要时可开启
        # 'django.request': {
        #     'handlers': ['null'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
    },
    # 设置默认的root handle 用于将开发手动输出的日志输出到指定文件中
    'root': {
        'level': 'DEBUG',
        'handlers': ['debug_file_handler', 'info_file_handler', 'error_file_handler']
    }
}