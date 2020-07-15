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


def signal_handler(signal,frame):
    print('\n bye bye')
    sys.exit()


app_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(os.path.join(app_path, "base_django_api"))


define('port', default=6000, type=int, help='run server')

def main():
    tornado.options.parse_command_line()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_django_api.settings')
    wsgi_app = tornado.wsgi.WSGIContainer(get_wsgi_application())
    http_server = tornado.httpserver.HTTPServer(wsgi_app, xheaders=True)
    http_server.listen(options.port)
    http_server.start(cpu_count())
    print("""[django-tornado-server]Wellcome...
Starting development server at http://%s:%s/       
Quit the server with CTRL+C.""" % ('127.0.0.1', str(options.port)))
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    signal.signal(signal.SIGINT,signal_handler)
    main()
