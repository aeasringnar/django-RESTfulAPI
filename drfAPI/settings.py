"""
Django settings for drfAPI project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from datetime import timedelta
from django.utils.translation import gettext_lazy as _


# config environment default dev
CURRENT_ENV = os.getenv('ENV', 'dev')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MY_APP_TEMPLATE = Path.joinpath(BASE_DIR, 'my_app_template')
MY_APPS_DIR = Path.joinpath(BASE_DIR, 'apps')
UPLOAD_DIR = Path.joinpath(BASE_DIR, 'media', 'upload')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g7!-t_sp)c$lpy4%oq)kv95$b&1+51=6d+0elqui%*b)^^!o#s'
AES_KEY = '16ed9ecc7d9011eab9c63c6aa7c68b67'
INTERFACE_TIMEOUT = 60
DISPATCH_KEYS = ['admin4b67e4c11eab49a3c6aa7c68b67', 'mobile347e4c11eab49a3c6aa7c68b67', 'mini235a7e4c11eab49a3c6aa7c68b67']


ALLOWED_HOSTS = [
    '*'
]


# cors config
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS= True
CORS_ALLOW_HEADERS = [
    '*'
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'startmyapp',
    'corsheaders',
    'rest_framework',
    'drf_yasg',
    'django_filters',
    'django_celery_results',
    'apps.user',
    'apps.public',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # 国际化中间件
    "corsheaders.middleware.CorsMiddleware", # 解决跨域中间件
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'extensions.MiddleWares.PUTtoPATCHMiddleware',
    'extensions.MiddleWares.LogMiddleware',
    # 'extensions.MiddleWares.PermissionMiddleware',
    'extensions.MiddleWares.FormatReturnJsonMiddleware',
]


ROOT_URLCONF = 'drfAPI.urls'
# RuntimeError: You called this URL via POST, but the URL doesn't end in a slash and you have APPEND_SLASH set. 
APPEND_SLASH=False 


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path.joinpath(BASE_DIR, 'templates')],
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


WSGI_APPLICATION = 'drfAPI.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/3.2/topics/i18n/
LOCALE_PATHS = [
    Path.joinpath(Path.joinpath(BASE_DIR, 'i18n'), 'locale')
]
LANGUAGES = [
    ('en', _('英语')),
    ('zh-hans', _('简体中文')),
]
LANGUAGE_CODE = 'zh-hans'  # 默认使用中文
TIME_ZONE = 'Asia/Shanghai'  # 中文时区
USE_I18N = True
USE_L10N = True
USE_TZ = False  # 不使用UTC格式时间


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    # 指定文件目录，BASE_DIR指的是项目目录，static是指存放静态文件的目录。
    os.path.join(BASE_DIR , 'static'),
]
# 迁移静态文件的目录,这个是线上是需要使用的 python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR , 'static/static')


# 媒体文件位置
MEDIA_URL = '/media/'
MEDIA_ROOT = Path.joinpath(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "SERIALIZER": "django_redis.serializers.msgpack.MSGPackSerializer",
            # "PASSWORD": ""
        }
    },
    "redis_cli": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# django rest framework config
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
    'EXCEPTION_HANDLER': 'extensions.ExceptionHandle.base_exception_handler',
    # DRF返回response定制json
    'DEFAULT_RENDERER_CLASSES': (
        'extensions.RenderResponse.BaseJsonRenderer',
    ),
}


SWAGGER_SETTINGS = {
    # 使用这个时需要使用django-rest的admin 也就是需要配置 url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 'LOGIN_URL': 'rest_framework:login',
    # 'LOGOUT_URL': 'rest_framework:logout',
    # 自定义swagger的路由tag
    'DEFAULT_GENERATOR_CLASS': 'extensions.MyCustomSwagger.BaseOpenAPISchemaGenerator',
    # 'DEFAULT_AUTO_SCHEMA_CLASS': 'configs.swagger.CustomSwaggerAutoSchema',
    'DEFAULT_AUTO_SCHEMA_CLASS': 'extensions.MyCustomSwagger.MySwaggerAutoSchema',
    'DEFAULT_PAGINATOR_INSPECTORS': [
        'extensions.MyCustomPagResponse.MyDjangoRestResponsePagination',
    ],
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


JWT_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7), # 指定token有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7), # 指定刷新token有效期
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHMS': ['HS256'], # 指定加密的哈希函数
    'SIGNING_KEY': SECRET_KEY, # jwt的密钥
    'VERIFY_SIGNATURE': True, # 开启验证密钥
    'VERIFY_EXP': True, # 开启验证token是否过期
    'AUDIENCE': None,
    'ISSUER': None,
    'LEEWAY': 0,
    'REQUIRE': ['exp'],
    'AUTH_HEADER_TYPES': 'Bearer',
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}


# Celery配置
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
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/3'
# 指定存储结果的地方，支持使用rpc、数据库、redis等等，具体可参考文档 # CELERY_RESULT_BACKEND = 'db+mysql://scott:tiger@localhost/foo' # mysql 作为后端数据库
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/4'
# 使用django数据库存储结果 来自 django_celery_results
CELERY_RESULT_BACKEND = 'django-db'
# 结果的缓存配置 来自 django_celery_results
CELERY_CACHE_BACKEND = 'django-cache'
# 设置任务过期时间 默认是一天，为None或0 表示永不过期
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
# 设置异步任务结果永不过期，如果不设置的话，每天04点celery会自动清空过期的异步任务结果
CELERY_RESULT_EXPIRES = 0
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


# 媒体文件格式限制
MEDIA_FILE_CHECK = ('png', 'jpg', 'jpeg', 'gif', 'svg', 'mp4', 'mkv', 'avi', 'mp3', 'webm', 'wav', 
                    'ogg', 'glb', 'gltf', 'vrm', 'txt', 'pdf', 'epub', 'mobi', 'azw3')
# 媒体文件大小限制
MEDIA_FILE_SIZE = 1024 * 1024 * 64
# 图像文件大小限制
IMAGE_FILE_SIZE = 1024 * 1024 * 8
IMAGE_FILE_CHECK = ('png', 'jpg', 'jpeg', 'gif', 'svg')
VIDEO_FILE_CHECK = ('mp4', 'mkv', 'avi')
SOUND_FILE_CHECK = ('mp3', 'webm', 'wav', 'ogg')
MODEL_FILE_CHECK = ('glb', 'gltf', 'vrm')
EBOOK_FILE_CHECK = ('txt', 'pdf', 'epub', 'mobi', 'azw3')


# 限制每个接口请求频次
MINUTE_HZ = 30


# 全文检索配置
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
# 使用自定义的自动更新索引类
HAYSTACK_SIGNAL_PROCESSOR = 'extensions.CustomRealtimeSignal.RealtimeSignalProcessor'


if CURRENT_ENV == 'dev':
    from configs.dev.settings import *
else:
    from configs.prod.settings import *