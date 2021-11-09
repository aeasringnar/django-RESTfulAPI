import os, sys, datetime, random
from datetime import timedelta
# import pymysql
# pymysql.install_as_MySQLdb()
CURRENT_ENV = os.getenv('ENV', 'dev')


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
CONF_FILE_PATH = os.path.join(BASE_DIR, 'config')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0b($)a_$n$!grvsj!pob$5z4(q+u3fo_)aoz!g)3^=pk@7g770sdfgertgsdf'
INTERFACE_KEY = '16ed9ecc7d9011eab9c63c6aa7c68b67'
INTERFACE_TIMEOUT = 60
DISPATCH_KEYS = ['admin4b67e4c11eab49a3c6aa7c68b67', 'mobile347e4c11eab49a3c6aa7c68b67', 'mini235a7e4c11eab49a3c6aa7c68b67']


# SECURITY WARNING: don't run with debug turned on in production!
# 如果出现报错为：django.template.response.ContentNotRenderedError: The response content must be rendered before it can be accessed.
# 那么很有可能是数据库的问题：在jwt的认证模块中，搜索用户的位置查找可能的问题
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
    # DRF异常定制处理方法
    'EXCEPTION_HANDLER': 'utils.exceptionHandle.base_exception_handler',
    # DRF返回response定制json
    'DEFAULT_RENDERER_CLASSES': (
        'utils.rendererresponse.BaseJsonRenderer',
    ),
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




# 根据环境变量导入不同的配置
if CURRENT_ENV == 'dev':
    from config.dev_settings import *
else:
    from config.prod_settings import *