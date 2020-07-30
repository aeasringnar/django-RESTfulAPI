
class Router(object):
    def db_for_read(self, model, **hints):
        return 'read'

    def db_for_write(self, model, **hints):
        return 'default'
