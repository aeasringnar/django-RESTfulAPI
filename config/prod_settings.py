import os


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
'''
生产环境的配置
'''
# 关闭调试
DEBUG = False
# 是否查看运行时的 SQL语句
SHOWSQL = False



# 生产环境使用mysql数据库
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


# 微信开发配置
WECHAT_MCHID = '微信支付平台商户号'
WECHAT_KEY = '微信支付平台秘钥'
WECHAT_PAY_NOTIFY_URL = '微信支付异步通知url'
WECHAT_MINI_APPID = '微信小程序appid'  
WECHAT_MINI_SECRET = '微信小程序secret'
WECHAT_APP_APPID = '微信开放平台APP_appid'
WECHAT_APP_SECRET = '微信开放平台APP_secret'
# 微信企业付款相关证书
CERT_PATH = os.path.join(PROJECT_DIR, 'utils/cert/apiclient_cert.pem')
CERT_KEY_PATH = os.path.join(PROJECT_DIR, 'utils/cert/apiclient_key.pem')


# 支付宝支付
ALIPAY_APPID = '支付宝appid'
# 支付宝商户私钥
PRIVATE_KEY_PATH = os.path.join(PROJECT_DIR, 'utils/ali_keys/rsa_private_key.pem')
# 支付宝支付公钥
ALIPUB_KEY_PATH = os.path.join(PROJECT_DIR, 'utils/ali_keys/ali_public_key.text')
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
SERVER_NAME = 'www.line.com'


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