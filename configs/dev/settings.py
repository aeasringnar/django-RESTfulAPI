from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# 是否查看运行时的 SQL语句
SHOWSQL = False
# 设置服务host
SERVER_NAME = ''


# dev atabase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# 日志配置
LOGGING = {
    'version': 1,  # 指明dictConnfig的版本
    'disable_existing_loggers': False,  # 表示是否禁用所有的已经存在的日志配置
    'formatters': {  # 格式器
        'verbose': {  # 详细
            'format': '[%(levelname)s] %(asctime)s %(module)s.%(funcName)s [%(process)d:%(thread)d] - %(filename)s[line:%(lineno)d] %(message)s'
        },
        'standard': {  # 标准
            'format': '[%(asctime)s] %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        },
        "debug": { # 调试
            "format": "[%(asctime)s] [%(process)d:%(thread)d] %(filename)s[line:%(lineno)d] (%(name)s)[%(levelname)s] %(message)s",
        },
        "json": {
            "()": "extensions.JsonFormater.JSONFormatter"
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
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
        'django.request': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    # 设置默认的root handle 用于将开发手动输出的日志输出到指定文件中
    'root': {
        'level': 'DEBUG',
        'handlers': ['debug_file_handler', 'info_file_handler', 'error_file_handler']
    }
}