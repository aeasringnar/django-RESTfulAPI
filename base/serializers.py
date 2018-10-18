from rest_framework import serializers
from .models import *

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id','name','zhname')

class UserSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    class Meta:
        model = User
        fields = ('id','name','phone','email','gender','password','birthday','info','addr','qq','weixin','group','image_url')

class DoubanZufangSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubanZufang
        fields = ('id','title','href')
