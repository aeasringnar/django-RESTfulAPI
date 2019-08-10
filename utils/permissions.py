from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser
from rest_framework.permissions import BasePermission
from user.models import GroupAuth
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


class BaseAuthPermission(object):

    def white_list_check(self, auth_name):
        # 无需登录白名单
        if auth_name in ['login', 'register', 'getcode', 'confdict', ]:
            return True
        else:
            return False
    
    def need_auth_list_check(self, auth_name):
        # 只需登录白名单
        if auth_name in ['userinfo', 'export*', ]:
            return True
        else:
            return False

    def has_permission(self, request, view):
        # 动态权限层
        print('请求的path：', request.path)
        # print('请求的path：', request.path.split('/')[1])
        auth_name = request.path.split('/')[1]
        if str(request.user) == 'AnonymousUser':
            return self.white_list_check(auth_name)
        if request.user.group.id == 1:
            return True
        if self.white_list_check(auth_name):
            return True
        if self.need_auth_list_check(auth_name):
            return bool(request.auth)
        admin_auth = GroupAuth.objects.filter(object_name=auth_name).first()
        if not admin_auth and request.user.group.id != 1:
            return False
        
        if view.action == 'list' or view.action == 'retrieve':
            # 查看权限
            return bool(request.auth and admin_auth.auth_list == True)
        elif view.action == 'create':
            # 创建权限
            return bool(request.auth and admin_auth.auth_create == True)
        elif view.action == 'update' or view.action == 'partial_update':
            # 修改权限
            return bool(request.auth and admin_auth.auth_update == True)
        elif view.action == 'destroy':
            # 删除权限
            return bool(request.auth and admin_auth.auth_destroy == True)
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # 动态权限层
        print('请求的path：', request.path)
        # print('请求的path：', request.path.split('/')[1])
        auth_name = request.path.split('/')[1]
        if str(request.user) == 'AnonymousUser':
            return self.white_list_check(auth_name)
        if request.user.group.id == 1:
            return True
        if self.white_list_check(auth_name):
            return True
        if self.need_auth_list_check(auth_name):
            return bool(request.auth)
        admin_auth = GroupAuth.objects.filter(object_name=auth_name).first()
        if not admin_auth and request.user.group.id != 1:
            return False
        
        if view.action == 'list' or view.action == 'retrieve':
            # 查看权限
            return bool(request.auth and admin_auth.auth_list == True)
        elif view.action == 'create':
            # 创建权限
            return bool(request.auth and admin_auth.auth_create == True)
        elif view.action == 'update' or view.action == 'partial_update':
            # 修改权限
            return bool(request.auth and admin_auth.auth_update == True)
        elif view.action == 'destroy':
            # 删除权限
            return bool(request.auth and admin_auth.auth_destroy == True)
        else:
            return False