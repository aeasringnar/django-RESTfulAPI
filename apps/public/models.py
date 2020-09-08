from django.db import models
from soft_delete_new.models import SoftDeleteModel
import datetime
'''
objects 返回没有删除的所有数据
all_objects 返回所有数据
delete 删除数据，假删
undelete 恢复假删数据
模型字段类型：
models.CharField() # 字符串类型
models.TextField() # 文本类型
models.IntegerField() # int类型
models.BooleanField() # bool类型
models.NullBooleanField() # 允许为空的bool类型
models.DateField() # 日期类型 年月日
models.DecimalField() # 金额类型 可以指定长度和小数位数 max_digits=15, decimal_places=2, 总长度15位，小数位为2
models.EmailField() # 邮箱类型
models.FloatField() # 浮点数类型
models.TimeField() # 时间类型
当想指定表主键时，例如想指定主键为UUID：id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
models.ForeignKey(OtherModel, on_delete=models.PROTECT, verbose_name='label', related_name='related_name') # 外键类型
models.OneToOneField(OtherModel, on_delete=models.PROTECT, verbose_name='label', related_name='related_name') # 一对一的外键类型
models.ManyToManyField(OtherModel, verbose_name='label', blank=True, related_name='related_name') # 多对多类型，django会自己维护一个中间表。如果需求更多，可以自己使用中间表实现多对多关系
on_delete属性选项的意义：
models.PROTECT：当外键数据删除时，指向外键的的数据不删除。
models.CASCADE：当外键数据删除时，指向外键的数据一起删除。
models.SET_NULL：当外键数据删除时，指向外键的数据该列设置为null。
models.SET_DEFAULT：当外键数据删除时，指向外键的数据该列恢复默认值。
models.SET(自定义方法)：当外键数据删除时，指向外键的数据使用自定义方法来设置值。具体可参考官方文档。

字段常用options：
unique=True # 设置唯一性约束也是唯一索引
db_index=True # 设置普通索引
null = True # 允许值为空
blank = True # 允许键为空，指定的字段可以不传
choices = ((0,'男'),('1','女'),) # 选项类型
default = 1 # 指定默认值
verbose_name = '描述' # 指定label 或字段描述
auto_now_add = True # 在创建的时候插入时间
auto_now = True # 每次修改都会更新时间
max_length = 255 # 指定字段容量长度，CharField必须要指定

元类Meta常用options：
abstract = True # 表示该模型是抽象基类，其他模型可以继承这个模型。
app_label = 'myapp' # 声明模型所属的app
db_table = 'A_Table' # 自定义数据表在数据库中的名称
verbose_name = 'A表' # 自定义数据表的表述，官方叫 对象的人类可读名称 单数形式
verbose_name_plural = verbose_name # 对verbose_name的复数描述
ordering = ['-create_date'] # 指定数据的默认排序，该例表示根据创建时间倒序(不加-为升序)。
unique_together = [['name1', 'name2']] # 设置联合唯一性约束，可以设置多个，为了方便起见，unique_together在处理一组字段时可以是一个一维列表。
index_together = [['name1', 'name2']] # 设置联合索引，可以设置多个，为了方便起见，index_together在处理一组字段时可以是一个一维列表。
indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['first_name'], name='first_name_idx'),
        ]  # 定义索引列表
'''
class BigDataFilterManager(models.Manager):
    
    def all(self, filter_time=None):
        if filter_time:
            if ',' in filter_time:
                start_time = datetime.datetime.strptime(filter_time.split(',')[0] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                end_time = datetime.datetime.strptime(filter_time.split(',')[1] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                return super().all().filter(create_time__gte=start_time, create_time__lte=end_time)
            return super().all()
        return super().all()


class BaseModel(models.Model):
    # sort = models.IntegerField(default=1, verbose_name='排序')
    # desc = models.TextField(default='', blank=True, verbose_name='描述')
    # sort_time = models.DateTimeField(auto_now_add=True, verbose_name='排序时间')
    create_time = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, db_index=True, verbose_name='更新时间')
    # objects = BigDataFilterManager()  # 是否开放大数据时的日期过滤

    class Meta:
        abstract = True


class ConfDict(SoftDeleteModel, BaseModel):
    dict_type_choices = (
        (0, '类型一'),
        (1, '类型二'),
        (2, '类型三'),
    )
    dict_title = models.CharField(max_length=255, verbose_name='字典标题')
    # dict_content = models.TextField(default='', blank=True, verbose_name='字典内容')
    dict_key = models.IntegerField(default=0, verbose_name='字典键值')
    dict_type = models.IntegerField(default=0, choices=dict_type_choices, verbose_name='字典类型')

    class Meta:
        db_table = 'A_ConfDict_Table'
        verbose_name = '系统字典表'
        verbose_name_plural = verbose_name