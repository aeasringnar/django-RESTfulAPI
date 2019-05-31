from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueValidator
from .models import *
import time
import datetime


class BaseModelSerializer(serializers.Serializer):
    sort_time = serializers.DateTimeField(label='排序时间', format='%Y-%m-%d %H:%M:%S')
    created = serializers.DateTimeField(label='创建时间', format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated = serializers.DateTimeField(label='更新时间', format='%Y-%m-%d %H:%M:%S', read_only=True)



# def get_ObjectFlow(type):
#     if type == 0:
#         approval_flow = ApprovalFlow.objects.filter(flow_name='请假审批').first()
#     elif type == 1:
#         approval_flow = ApprovalFlow.objects.filter(flow_name='出差审批').first()
#     else:
#         return None
#     if approval_flow:
#         approval_flow_fucs = ApprovalFlowFuc.objects.filter(
#             approval_flow=approval_flow.id)
#         object_flow = ObjectFlow()
#         object_flow.flow_name = approval_flow.flow_name
#         object_flow.save()
#         for item in approval_flow_fucs:
#             object_flow_fuc = ObjectFlowFuc()
#             object_flow_fuc.flowfuc_grade = item.flowfuc_grade
#             object_flow_fuc.object_flow = object_flow
#             object_flow_fuc.user = item.user
#             if object_flow_fuc.flowfuc_grade == 1:
#                 object_flow_fuc.upper_flow_result = 1
#             object_flow_fuc.save()
#         return object_flow
#     else:
#         return None


# class CurrentUser(object):
#     def set_context(self, serializer_field):
#         self.user_obj = serializer_field.context['request'].user

#     def __call__(self):
#         return self.user_obj

# class AddUserSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
#                                      validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])
#     phone = serializers.CharField(label="手机号", help_text="手机号", required=True, allow_blank=False,
#                                      validators=[UniqueValidator(queryset=User.all_objects.all(), message="手机号已经存在")],
#                                      error_messages={"required": '手机号不能为空', 'blank': '手机号不能为空', 'null': '手机号不能为空'})
#     object_flow = serializers.PrimaryKeyRelatedField(read_only=True)
#     user = serializers.HiddenField(default=CurrentUser())
#     order_int = serializers.SerializerMethodField(label='订单数')
#     oilcan_datas = DepotUseOilcanDataSerializer(read_only=True, many=True) # related_name
#     start_date = serializers.DateTimeField(label='开始日期', format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d'], required=False, allow_null=True)

#     class Meta:
#         model = User
#         fields = '__all__' # or exclude = ('deleted',) or fields = ['company','username',]
#         read_only_fields = ('user', 'object_flow',)
    
#     def validate(self, attrs):
#         flow_obj = get_ObjectFlow(0)
#         if not flow_obj:
#             raise serializers.ValidationError("运输合同审批流不存在")
#         attrs['object_flow'] = flow_obj
#         return attrs
    
#     def get_order_int(self, obj):
#         num = 0
#         contract_datas = Order.objects.filter(transportContract_id=obj.id)
#         num = len(contract_datas)
#         return num
