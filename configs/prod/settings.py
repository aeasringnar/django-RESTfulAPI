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