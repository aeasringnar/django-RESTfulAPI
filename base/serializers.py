from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from .models import *
import time, datetime

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id','name','zhname')




class UserSerializer(serializers.ModelSerializer):
    updated = SerializerMethodField()
    created = SerializerMethodField()
    group = GroupSerializer()
    class Meta:
        model = User
        fields = ('id','name','phone','email','gender','password','birthday','info','addr','qq','weixin','group','image_url','sort','updated','created')
    
    def get_updated(self,obj):
        if obj.updated:
            return time.strftime('%Y-%m-%d %H:%M',time.strptime(str(obj.updated),'%Y-%m-%d %H:%M:%S.%f'))
        else:
            return ''
    def get_created(self,obj):
        if obj.created:
            return time.strftime('%Y-%m-%d %H:%M',time.strptime(str(obj.created),'%Y-%m-%d %H:%M:%S.%f'))
        else:
            return ''

