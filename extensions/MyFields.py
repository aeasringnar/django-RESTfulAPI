from datetime import datetime
from django.db.models import BigIntegerField
from utils.MyDateTime import MyDateTime


class TimestampField(BigIntegerField):
    
    description = "Custom timestamp field."
    
    def __init__(self, verbose_name=None, name=None, auto_now=False,
                 auto_now_add=False, **kwargs):
        self.auto_now, self.auto_now_add = auto_now, auto_now_add
        if auto_now or auto_now_add:
            kwargs['editable'] = False
            kwargs['blank'] = True
        super().__init__(verbose_name, name, **kwargs)
    
    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            value = MyDateTime.datetime_to_timestamp(datetime.now())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)