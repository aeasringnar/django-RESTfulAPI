from cProfile import label
import uuid
import six
from datetime import datetime
from collections import Counter
from django.db import models, router, transaction
from django.db.models import signals, sql, Manager
from django.contrib.admin.utils import NestedObjects
from django.core.exceptions import FieldDoesNotExist
from operator import attrgetter
from django.core.validators import MaxValueValidator, MinValueValidator
from utils.MyDateTime import MyDateTime
from extensions.MyFields import TimestampField


__all__ = ['BaseModel']


class BigDataFilterManager(Manager):
    '''用于进行时间过滤数据'''
    
    def all(self, filter_time=None):
        if filter_time:
            if ',' in filter_time:
                start_time = MyDateTime.datetime_timestamp(datetime.strptime(filter_time.split(',')[0] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
                end_time = MyDateTime.datetime_timestamp(datetime.strptime(filter_time.split(',')[1] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
                return super().all().filter(create_timestamp__gte=start_time, update_timestamp__lte=end_time)
            return super().all()
        return super().all()


class SoftDeleteHelper():
    def __init__(self, using='default', delete_type='soft_delete'):
        self.using = using
        self.delete_type = delete_type

    def collect_objects(self, objs):
        '''
        Collect all related objects
        '''
        collector = NestedObjects(using=self.using)
        collector.collect(objs)

        if self.delete_type == 'soft_delete':
            collector = self.get_un_soft_deleted_objects(collector)

        return collector

    def get_un_soft_deleted_objects(self, collector):
        '''filter all those objects from collector which are already
        soft-deleted'''
        for model, instances in collector.data.items():
            try:
                if model._meta.get_field("deleted"):
                    collector.data[model] = set(filter(lambda x: not x.deleted,
                                                instances))
            except FieldDoesNotExist:
                # if deleted field does not exist in model, do nothing
                pass
        return collector

    def sort_all_objects(self, collector):
        '''
        If possible, bring the models in an order suitable for databases that
        don't support transactions or cannot defer constraint checks until the
        end of a transaction.
        '''
        for model, instances in collector.data.items():
            collector.data[model] = sorted(instances, key=attrgetter("pk"))
        collector.sort()

    def sql_model_wise_batch_update(self, model, instances, deleted=None):
        query = sql.UpdateQuery(model)
        pks = [obj.pk for obj in instances]
        query.update_batch(pks,
                           {'deleted': deleted, 'update_timestamp': MyDateTime.datetime_timestamp(datetime.now())}, self.using)

    def sql_hard_delete(self, model, instances):
        query = sql.DeleteQuery(model)
        query.delete_batch([obj.pk for obj in instances], self.using)

    def send_signal(self, model, instances, signal_type):
        '''
        Handle pre/post delete/save signal callings
        '''
        if not model._meta.auto_created:
            for obj in instances:
                if signal_type.__contains__('save'):
                    getattr(signals, signal_type).send(
                            sender=model, instance=obj,
                            created=False, using=self.using
                    )
                else:
                    getattr(signals, signal_type).send(
                            sender=model, instance=obj, using=self.using
                    )

    @transaction.atomic
    def do_work(self, objs):
        '''
        Method, call all helper methods to do soft-delete/undelete or
        hard-delete
        '''
        if not objs:
            # no object to delete/undelete
            return None
        # collect all related objects
        collector = self.collect_objects(objs)
        # sort collected objects
        self.sort_all_objects(collector)

        deleted_counter = Counter()
        # soft/hard-delete all nested instnaces in batch - model-wise
        if self.delete_type == 'hard_delete':
            return collector.delete()
        for model, instances in six.iteritems(collector.data):
            # send pre-delete signals
            if self.delete_type == 'soft_delete':
                self.send_signal(model, instances, "pre_delete")
            else:
                self.send_signal(model, instances, "pre_save")
            try:
                if self.delete_type == 'soft_delete':
                    self.sql_model_wise_batch_update(model, instances, deleted=uuid.uuid4())
                else:
                    self.sql_model_wise_batch_update(model, instances, deleted=None)
                deleted_counter[model._meta.model_name] += len(instances)
            except FieldDoesNotExist:
                # hard-delete instnaces of those model that are not made to
                # soft-delete
                self.sql_hard_delete(model, instances)
                deleted_counter[model._meta.model_name] += len(instances)

            # send post-delete signals
            if self.delete_type == 'soft_delete':
                self.send_signal(model, instances, "post_delete")
            else:
                self.send_signal(model, instances, "post_save")
        return sum(deleted_counter.values()), dict(deleted_counter)


class SoftDeleteQuerySet(models.QuerySet):

    @transaction.atomic
    def delete(self, using=None):
        '''setting deleted attribtue to new UUID', also soft-deleting all its
        related objects if they are on delete cascade'''
        using = using or "default"

        assert self.query.can_filter(), \
            "Cannot use 'limit' or 'offset' with delete."
        try:
            if self._fields is not None:
                raise TypeError("Cannot call delete() after .values() or\
                 .values_list()")
        except AttributeError:
            pass

        helper = SoftDeleteHelper(using=using, delete_type='soft_delete')
        return helper.do_work(self)

    @transaction.atomic
    def undelete(self, using=None):
        '''setting deleted attribtue to True', also soft-deleting all its
        related objects if they are on delete cascade'''
        using = using or "default"

        assert self.query.can_filter(), \
            "Cannot use 'limit' or 'offset' with delete."

        try:
            if self._fields is not None:
                raise TypeError("Cannot call delete() after .values() or\
                                .values_list()")
        except AttributeError:
            pass

        helper = SoftDeleteHelper(using=using, delete_type='soft_undelete')
        return helper.do_work(self)

    @transaction.atomic
    def hard_delete(self, using=None):
        using = using or "default"

        assert self.query.can_filter(), \
            "Cannot use 'limit' or 'offset' with delete."

        try:
            if self._fields is not None:
                raise TypeError("Cannot call delete() after .values() or\
                                .values_list()")
        except AttributeError:
            pass
        helper = SoftDeleteHelper(using=using, delete_type='hard_delete')
        helper.do_work(self)

    def only_deleted(self):
        if self.deleted_also:
            return self.exclude(deleted=None)
        raise ValueError('only_deleted can only be called with all_objects')


class SoftDeleteManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.deleted_also = kwargs.pop('deleted_also', False)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        '''return all unsoft-deleted objects if deleted_also is False'''
        # return super(SoftDeleteManager, self).get_queryset(
        #                                         ).filter(deleted=False)
        if self.deleted_also:
            return SoftDeleteQuerySet(self.model)
        return SoftDeleteQuerySet(self.model).filter(deleted=None)

    def only_deleted(self):
        if self.deleted_also:
            return self.exclude(deleted=None)
        raise ValueError('only_deleted can only be called with all_objects')


class BaseModel(models.Model):
    '''
    Abstract model that holds:
      1. one attribute:
        deleted - default is False, when object is soft-deleted it is set to
        new UUID

      2. objects manager which have following methods:
        delete() - to soft delete instance
        hard_delete() - to hard delete instance
      3. all_objects manager which have following methods:
        delete() - to soft delete instance
        hard_delete() - to hard delete instance
        only_deleted() - to return all those instances that are soft-deleted
        undelete() - to undelete soft deleted objects


    It override default method delete(), that soft-deletes the object by
    setting deleted to new UUID.
    '''
    deleted = models.UUIDField(default=None, null=True, blank=True, verbose_name='删除标志')
    remark = models.TextField(max_length=1024, default='', blank=True, verbose_name='备注')
    sort_timestamp = TimestampField(auto_now_add=True, db_index=True, validators=[MinValueValidator(limit_value=0)], verbose_name='排序时间戳，默认等于创建时间戳')
    create_timestamp = TimestampField(auto_now_add=True, db_index=True, validators=[MinValueValidator(limit_value=0)], verbose_name='创建时间戳')
    update_timestamp = TimestampField(auto_now=True, db_index=True, validators=[MinValueValidator(limit_value=0)], verbose_name='更新时间戳')

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(deleted_also=True)

    @transaction.atomic
    def delete(self, using=None):
        '''
        Setting deleted attribtue to new UUID',
        also if related objects are on delete cascade:
          they will be soft deleted if those related objects have soft deletion
          capability
          else they will be hard deleted.
        '''
        using = using or router.db_for_write(self.__class__, instance=self)

        helper = SoftDeleteHelper(using=using, delete_type='soft_delete')
        return helper.do_work([self])

    @transaction.atomic
    def undelete(self, using=None):
        '''setting deleted attribtue to False of current object and all its
        related objects if they are on delete cascade'''
        using = using or router.db_for_write(self.__class__, instance=self)
        helper = SoftDeleteHelper(using=using, delete_type='soft_undelete')
        return helper.do_work([self])

    @transaction.atomic
    def hard_delete(self, using=None):
        '''setting deleted attribtue to False of current object and all its
        related objects if they are on delete cascade'''
        using = using or router.db_for_write(self.__class__, instance=self)
        helper = SoftDeleteHelper(using=using, delete_type='hard_delete')
        return helper.do_work([self])

    class Meta:
        abstract = True