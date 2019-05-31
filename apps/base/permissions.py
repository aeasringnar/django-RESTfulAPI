from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser
from rest_framework.permissions import BasePermission
'''
mixins.CreateModelMixin	    create   POST	  创建数据
mixins.RetrieveModelMixin	retrieve GET	  检索数据
mixins.UpdateModelMixin	    update   PUT	  更新数据
                            perform_update PATCH 更新数据
mixins.DestroyModelMixin	destroy  DELETE	  删除数据
mixins.ListModelMixin	    list     GET	  获取数据
'''

class JWTAuthPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.auth)

    def has_object_permission(self, request, view, obj):
        return True


class AllowAllPermission(object):

    def has_permission(self, request, view):
        return True