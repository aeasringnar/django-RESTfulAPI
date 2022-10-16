
name = 'drfAPI'
wsgi_app = 'drfAPI.asgi:application'
bind = '0.0.0.0:8080'
workers = 2
threads = 2
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 2000 # 协程并发模式下还存在一个并发文件日志写入的问题，就是并发时会导致日志文件重写、混乱写入等问题，待解决
# 将日志全部交给框架内的日志输出处理 使用uvicorn worker 还是存在一些问题，日志无法按照预期的输出，wsgi模式下无影响。
# accesslog = f'./logs/{name}_access.log'
# access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# errorlog = f'./logs/{name}_error.log'
loglevel = 'error'