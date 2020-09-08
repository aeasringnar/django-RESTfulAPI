import os, sys, datetime, random
from datetime import timedelta
# import pymysql
# pymysql.install_as_MySQLdb()


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0b($)a_$n$!grvsj!pob$5z4(q+u3fo_)aoz!g)3^=pk@7g770sdfgertgsdf'
INTERFACE_KEY = '16ed9ecc7d9011eab9c63c6aa7c68b67'
INTERFACE_TIMEOUT = 60
DISPATCH_KEYS = ['admin4b67e4c11eab49a3c6aa7c68b67', 'mobile347e4c11eab49a3c6aa7c68b67', 'mini235a7e4c11eab49a3c6aa7c68b67']


# SECURITY WARNING: don't run with debug turned on in production!
# 如果出现报错为：django.template.response.ContentNotRenderedError: The response content must be rendered before it can be accessed.
# 那么很有可能是数据库的问题：在jwt的认证模块中，搜索用户的位置查找可能的问题
DEBUG = True  # 开发时设置为True 线上环境设置为False
SHOWSQL = False # 是否查看运行时的 SQL语句
INTERNAL_IPS = [
    '127.0.0.1',
]


ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')


# 配置请求体大小100m 处理跨域的问题
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS= True
CORS_ALLOW_HEADERS = (
    '*'
)
CORS_ALLOW_HEADERS = (
    '*'
)
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework_swagger',
    'django_crontab',
    'django_filters',
    'drf_yasg',
    'django_celery_results',
    'debug_toolbar',
    'public.apps.PublicConfig',
    'user.apps.UserConfig',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # 解决跨域中间件
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', # debug 中间件
    'middleware.BaseMiddleWare.PUTtoPATCHMiddleware', # 将 put 请求转化为 patch 请求中间件
    'middleware.BaseMiddleWare.LogMiddleware', # 日志格式化中间件
    # 'middleware.BaseMiddleWare.PermissionMiddleware', # 增加接口检测中间件
    'middleware.BaseMiddleWare.FormatReturnJsonMiddleware', # response 格式化中间件
    'middleware.BaseMiddleWare.BlockUserMiddleware', # 冻结用户中间件
]


ROOT_URLCONF = 'base_django_api.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'base_django_api.wsgi.application'


'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
'''
# 使用mysql数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'base-api',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",  # 去除强制外键约束
            'charset': 'utf8mb4',
            'sql_mode': 'traditional'
        }
    }
}

'''
sql_mode
ANSI模式：宽松模式，对插入数据进行校验，如果不符合定义类型或长度，对数据类型调整或截断保存，报warning警告。
TRADITIONAL 模式：严格模式，当向mysql数据库插入数据时，进行数据的严格校验，保证错误数据不能插入，报error错误。用于事物时，会进行事物的回滚。
STRICT_TRANS_TABLES模式：严格模式，进行数据的严格校验，错误数据不能插入，报error错误。
'''


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = 'zh-hans'  #中文语言
TIME_ZONE = 'Asia/Shanghai'  #中文时区
USE_I18N = True
USE_L10N = True
USE_TZ = False  #不使用UTC格式时间



# STATIC_OSS_BASE_DIR = 'https://nbjice-h5.oss-cn-hangzhou.aliyuncs.com'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    # 指定文件目录，BASE_DIR指的是项目目录，static是指存放静态文件的目录。
    os.path.join(BASE_DIR , 'static'),
]
# 迁移静态文件的目录,这个是线上是需要使用的 python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR , 'static/static')


# 媒体文件位置
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# rest 相关配置
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    # ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'drf_renderer_xlsx.renderers.XLSXRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    # 格式化时间
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATETIME_INPUT_FORMATS': ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'),
    'DATE_FORMAT': '%Y-%m-%d',
    'DATE_INPUT_FORMATS': ('%Y-%m-%d',),
    'TIME_FORMAT': '%H:%M:%S',
    'TIME_INPUT_FORMATS': ('%H:%M:%S',),
}

# 使用redis缓存  缓存扩展：drf-extensions 使用redis异常，问题未知
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "SERIALIZER": "django_redis.serializers.msgpack.MSGPackSerializer",
            #"PASSWORD": ""
        }
    },
    "cache_redis": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# 缓存扩展：drf-extensions  缓存过期时间配置
# REST_FRAMEWORK_EXTENSIONS = {
#     'DEFAULT_CACHE_RESPONSE_TIMEOUT': 5
# }


'''
# Aliyun OSS
AliOSS_ACCESS_KEY_ID = "LTAI6hxpAQNHm0hE"
AliOSS_ACCESS_KEY_SECRET = "Iw7jlRBsutGR2PUgg0vnydRzXETCOX"
AliOSS_END_POINT = "oss-cn-hangzhou.aliyuncs.com"
AliOSS_BUCKET_NAME = "base-api"
AliOSS_BUCKET_ACL_TYPE = "public-read"  # private, public-read, public-read-write
# AliOSS_CNAME = ""  # 自定义域名，如果不需要可以不填写
# mediafile将自动上传
# AliOSS_DEFAULT_FILE_STORAGE = 'aliyun_oss2_storage.backends.AliyunMediaStorage'
# staticfile将自动上传
# AliOSS_STATICFILES_STORAGE = 'aliyun_oss2_storage.backends.AliyunStaticStorage'
'''


SWAGGER_SETTINGS = {
    # 使用这个时需要使用django-rest的admin 也就是需要配置 url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 'LOGIN_URL': 'rest_framework:login',
    # 'LOGOUT_URL': 'rest_framework:logout',
    'USE_SESSION_AUTH': False,
    # 'SHOW_EXTENSIONS': False,
    'DOC_EXPANSION': 'none',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}


# 定时任务
'''
*    *    *    *    * ：分别表示 分(0-59)、时(0-23)、天(1 - 31)、月(1 - 12) 、周(星期中星期几 (0 - 7) (0 7 均为周天))
crontab范例：
每五分钟执行    */5 * * * *
每小时执行     0 * * * *
每天执行       0 0 * * *
每周一执行       0 0 * * 1
每月执行       0 0 1 * *
每天23点执行   0 23 * * *
'''
CRONJOBS = [
    ('*/1 * * * *', 'public.crontabs.confdict_handle', ' >> /home/aea/my_project/gitee_project/django-RESTfulAPI/logs/confdict_handle.log'), # 注意：/tmp/base_api 目录要手动创建
]


# 日志配置
LOGGING = {
    'version': 1,  # 指明dictConnfig的版本
    'disable_existing_loggers': False,  # 表示是否禁用所有的已经存在的日志配置
    'formatters': {  # 格式器
        'verbose': {  # 详细
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'standard': {  # 标准
            'format': '[%(asctime)s] [%(levelname)s] %(message)s'
        },
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
    },
}


# Celery配置
from kombu import Exchange, Queue
# 设置任务接受的类型，默认是{'json'}
CELERY_ACCEPT_CONTENT = ['application/json']
# 设置task任务序列列化为json
CELERY_TASK_SERIALIZER = 'json'
# 请任务接受后存储时的类型
CELERY_RESULT_SERIALIZER = 'json'
# 时间格式化为中国时间
CELERY_TIMEZONE = 'Asia/Shanghai'
# 是否使用UTC时间
CELERY_ENABLE_UTC = False
# 指定borker为redis 如果指定rabbitmq CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
# 指定存储结果的地方，支持使用rpc、数据库、redis等等，具体可参考文档 # CELERY_RESULT_BACKEND = 'db+mysql://scott:tiger@localhost/foo' # mysql 作为后端数据库
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
# 使用django数据库存储结果
CELERY_RESULT_BACKEND = 'django-db'
# 结果的缓存配置
CELERY_CACHE_BACKEND = 'default'
# 设置任务过期时间 默认是一天，为None或0 表示永不过期
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
# 设置worker并发数，默认是cpu核心数
# CELERYD_CONCURRENCY = 12
# 设置每个worker最大任务数
CELERYD_MAX_TASKS_PER_CHILD = 100
# 使用队列分流每个任务
# CELERY_QUEUES = (
#     Queue("add", Exchange("add"), routing_key="task_add"),
#     Queue("mul", Exchange("mul"), routing_key="task_mul"),
#     Queue("xsum", Exchange("xsum"), routing_key="task_xsum"),
# )
# 配置队列分流路由，注意可能无效，需要在运行异步任务时来指定不同的队列
# CELERY_ROUTES = {
#     'public.tasks.add': {'queue': 'add', 'routing_key':'task_add'},
#     'public.tasks.mul': {'queue': 'add', 'routing_key':'task_add'},
#     'public.tasks.xsum': {'queue': 'add', 'routing_key':'task_add'},
#     # 'public.tasks.mul': {'queue': 'mul', 'routing_key':'task_mul'},
#     # 'public.tasks.xsum': {'queue': 'xsum', 'routing_key':'task_xsum'},
#     }
# 指定任务的位置
# CELERY_IMPORTS = (
#     'public.tasks',
# )
# 使用beat启动Celery定时任务
# CELERYBEAT_SCHEDULE = {
#     'add-every-10-seconds': {
#         'task': 'public.tasks.cheduler_task',
#         'schedule': 5,
#         'args': ('hello', )
#     },
# }
'''
运行的相关命令：
Celery：
celery -A poj worker -l info # 前台运行
nohup celery -A poj worker -l info > ./logs/celery.log 2>&1 & # 后台运行
celery multi start w1 -A poj -l info # 官方提供的后台运行策略，重启：celery multi restart w1 -A poj -l info；停止：celery multi stop w1 -A poj -l info # 使用这个命令的好处是可以在一台机器上运行多种worker
celery -A proj worker -P eventlet -c 1000 # 或者 celery -A proj worker -P gevent -c 1000  用协程支持并发 -c 用于这是并发的数量，使用协程时可以比较大。-P 用于设置使用协程来并发(协程并发由于线程并发)
celery -A proj beat -l info
Flower(Celery任务可视化插件)：
flower -A proj --port=5555 # 直接运行
celery flower -A proj --address=127.0.0.1 --port=5555 # 通过celery运行
flower -A django_cele_tasks --basic_auth=asd:123 # 指定登录名和密码，多个示例 celery flower --basic_auth=user1:password1,user2:password2
flower -A django_cele_tasks --auto_refresh=False # 关闭自动刷新
flower --conf=celeryconfig.py # 使用配置文件启动
nohup flower -A poj --address=0.0.0.0 --port=5555 --auto_refresh=False --basic_auth=admin:123 > ./logs/flower.log 2>&1 & # 后台运行
'''


# 微信开发配置
WECHAT_MCHID = '微信支付平台商户号'
WECHAT_KEY = '微信支付平台秘钥'
WECHAT_PAY_NOTIFY_URL = '微信支付异步通知url'
WECHAT_MINI_APPID = '微信小程序appid'  
WECHAT_MINI_SECRET = '微信小程序secret'
WECHAT_APP_APPID = '微信开放平台APP_appid'
WECHAT_APP_SECRET = '微信开放平台APP_secret'
# 微信企业付款相关证书
CERT_PATH = os.path.join(BASE_DIR, 'utils/cert/apiclient_cert.pem')
CERT_KEY_PATH = os.path.join(BASE_DIR, 'utils/cert/apiclient_key.pem')


# 支付宝支付
ALIPAY_APPID = '支付宝appid'
# 支付宝商户私钥
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'utils/ali_keys/rsa_private_key.pem')
# 支付宝支付公钥
ALIPUB_KEY_PATH = os.path.join(BASE_DIR, 'utils/ali_keys/ali_public_key.text')
ALIPAY_NOTIFY_URL = '支付宝支付异步通知url'


# 阿里短信设置
ALI_KEY = "your key"
ALI_SECRET = 'your secret'
ALI_REGION = 'your region'
ALI_SIGNNAME = 'your signame'
# 登录使用的信息模板
ALI_LOGOIN_CODE = 'your msg tempalte id'


# 极光推送配置
JPUSH_APPKEY = 'your key'
JPUSH_SECRET = 'your secret'


# 文件上传配置
FILE_CHECK = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'zip', 'rar', 'xls', 'xlsx', 'doc', 'docx', 'pptx', 'ppt', 'txt', 'pdf']
FILE_SIZE = 1024 * 1024 * 64
SERVER_NAME = '128.0.0.1'
