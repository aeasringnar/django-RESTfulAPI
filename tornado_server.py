import os
import sys
import signal
from tornado.options import options, define
from django.core.wsgi import get_wsgi_application
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
from multiprocessing import cpu_count
from django.conf import settings


def signal_handler(signal,frame):
    print('\n bye bye')
    sys.exit()


def main():
    try:
        if len(sys.argv) < 2:
            raise ValueError('参数异常，请尝试python tornado_server.py runserver 8080')
        elif sys.argv[1] == 'runserver':
            if len(sys.argv) != 3:
                raise ValueError('runserver选项参数错误！')
            if ':' in sys.argv[2]:
                host, port = sys.argv[2].split(':')
            else:
                port = sys.argv[2]
                host = '127.0.0.1'
            tornado.options.parse_command_line()
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_django_api.settings')
            wsgi_app = tornado.wsgi.WSGIContainer(get_wsgi_application())
            server = tornado.httpserver.HTTPServer(wsgi_app, xheaders=True)
            server.listen(int(port), host)
            if not settings.DEBUG:
                server.start(cpu_count())
            print("""[django-tornado-server]Wellcome...
Starting development server at http://%s:%s/       
Quit the server with CTRL+C.""" % (host, str(port)))
            tornado.ioloop.IOLoop.instance().start()
        else:
            raise ValueError('参数异常！')
    except Exception as e:
        print('发生异常：%s' % str(e))

if __name__ == '__main__':
    app_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(app_path, "base_django_api"))
    signal.signal(signal.SIGINT,signal_handler)
    main()