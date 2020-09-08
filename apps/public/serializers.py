from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from .models import *
import time
import datetime
'''
serializers 常用字段
name = serializers.CharField(required=False, label='描述', max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
name = serializers.EmailField(max_length=None, min_length=None, allow_blank=False)
name = serializers.FloatField(max_value=None, min_value=None)
name = serializers.IntegerField(max_value=None, min_value=None)
name = serializers.DateTimeField(format=api_settings.DATETIME_FORMAT, input_formats=None)
name = serializers.DateField(format=api_settings.DATE_FORMAT, input_formats=None)
name = serializers.BooleanField()
name = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=100))
name = serializers.DictField(child=<A_FIELD_INSTANCE>, allow_empty=True)  DictField(child=CharField())
Q(name__icontains=keyword) 内部是like模糊搜索
__gt 大于 
__gte 大于等于
__lt 小于 
__lte 小于等于
__in 在某某范围内
is null / is not null 为空/非空
.exclude(age=10) 查询年龄不为10的数据
'''


# 基本序列化器
class BaseModelSerializer(serializers.Serializer):
    # sort_time = serializers.DateTimeField(required=False, label='排序时间', format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d'],)
    create_time = serializers.DateTimeField(label='创建时间', format='%Y-%m-%d %H:%M:%S', read_only=True)
    update_time = serializers.DateTimeField(label='更新时间', format='%Y-%m-%d %H:%M:%S', read_only=True)


# 系统字典序列化器
class ConfDictSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfDict
        exclude = ('deleted',)



# def get_ObjectFlow(type):
#     '''
#     返回对象
#     '''
#     if type == 0:
#         approval_flow = TableClass.objects.filter(flow_name='请假审批').first()
#     elif type == 1:
#         approval_flow = TableClass.objects.filter(flow_name='出差审批').first()
#     else:
#         return None
#     if approval_flow:
#         object_flow = TableClass()
#         return object_flow
#     else:
#         return None


# class CurrentUser(object):
#     '''
#     返回指定的值
#     使用该方法可以做一些后端数据自动计算的工作
#     '''
#     def set_context(self, serializer_field):
#         self.user_obj = serializer_field.context['request'].user

#     def __call__(self):
#         return self.user_obj

# class AddUserSerializer(serializers.ModelSerializer):
#     # 在源头上防止出现重复数据
#     name = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
#                                      validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])
#     # 防止出现重复数据的同时，对数据进行验证
#     mobile = serializers.CharField(label="手机号", help_text="手机号", required=True, allow_blank=False,
#                                      validators=[UniqueValidator(queryset=User.all_objects.all(), message="手机号已经存在")],
#                                      error_messages={"required": '手机号不能为空', 'blank': '手机号不能为空', 'null': '手机号不能为空'})
#     # 将一个外键设为只读，防止前端传入值进来修改
#     object_flow = serializers.PrimaryKeyRelatedField(read_only=True)
#     # 在执行新增操作的时候，在前端隐藏user的传入，后端默认使用当前用户插入
#     # 第二种方法 user = serializers.HiddenField(default=serializers.CurrentUserDefault(), label='用户') 其实就是restframwork实现了CurrentUser
#     user = serializers.HiddenField(default=CurrentUser())
#     # 指定这个字段在返回给前端之前，也就是序列化时 可以按照指定的函数进行序列化
#     order_int = serializers.SerializerMethodField(label='订单数')
#     # 当有模型的外键指向当前模型时，可以通过related_name反向插入所有关联的子数据 接收的子的Serializer
#     oilcan_datas = DepotUseOilcanDataSerializer(read_only=True, many=True)
#     # 将对应的外键通过 父Serializer序列化后返回给前端
#     depart = ReturnDepartSerializer()
#     # 用于指定日期的输入格式、返回格式，注意可以在settings中统一设置后，可以省略这里的代码
#     start_date = serializers.DateTimeField(label='开始日期', format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d'], required=False, allow_null=True)

#     class Meta:
#         model = User
#         fields = '__all__' # __all__用于序列化所有字段 or exclude = ('deleted',)指定，某些字段不被序列化返回 or fields = ['company','username',]指定序列化的字段
#         read_only_fields = ('user', 'object_flow',) # 指定只读的字段，这样就不会被前端修改
#         validators = [UniqueTogetherValidator(queryset=Auth.objects.all(), fields=['auth_type',], message='该权限已经存在')] # 多字段联合唯一
    
#     def validate(self, attrs):
#         now_user = self.context['request'].user
#         # 查看前端传来的所有数据
#         print('查看attrs:', attrs)
#         # 查看前端是否有通过pk检索数据 来做出相应的改变
#         print('查看pk:', self.context['view'].kwargs.get('pk'))
#         # 在这里可以获取body参数
#         print('查看body参数：', self.context['request'].data)
#         flow_obj = get_ObjectFlow(0)
#         if not flow_obj:
#             raise serializers.ValidationError("审批流不存在")
#         attrs['object_flow'] = flow_obj
#         return attrs
    
#     def get_order_int(self, obj):
#         # 这种方法只会在返回时被调用
#         # 在这里可以通过GET参数 做一些返回操作 注意：只有在使用viewset里面才有效
#         print('查看GET参数：', self.context['request'].query_params)
#         num = 0
#         return num
'''
标识禁止序列化的字段，直接无视该字段的增删改查，一般用于字段被数据库或框架管理，例如是否被删除的标志字段。
exclude = ('deleted',)
序列化所有字段，所有字段默认都根据模型定义的验证规则进行验证，可以自定义其他辅助验证，或将某些字段对前端隐藏后端处理，对于需要返回给前端还得在后端处理的字段需要在放到read_only_fields内
fields = '__all__' 
指定序列化的字段，增删改查只能对这些字段生效
fields = ['field01','field01',]
设置只读的字段，被设置的字段不能被前端传来的值改变，，这些这可以在后端自己管理 在validate中管理
它表示对fields的补充，它补充了对fields指定字段做只读，应用场景是后端处理字段后返回给前端。
read_only_fields = ('field01', )
被HiddenField处理的字段，将会对前端无感，前端在增删改查时都将无感该字段
它也是对fields指定字段的补充，值得注意的是，如果对同一个字段使用HiddenField和read_only_fields，只有HiddenField有效
user = serializers.HiddenField(default=serializers.CurrentUserDefault(), label='所属用户')


1、前端新增或修改时 即不需要设置也不需要返回 使用 exclude 包含进去
2、前端新增时 即不需要设置也不需要返回 但需要后端设置值的 使用 HiddenField 因为 HiddenField 只在新增时有效
3、前端新增或修改时 不需要设置但需要返回的 使用 read_only_fields 包含进去
注意：需要的字段都要存在于 fields 被序列化字段中
'''