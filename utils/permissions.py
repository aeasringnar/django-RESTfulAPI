from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser
from rest_framework.permissions import BasePermission
from user.models import AuthPermission
'''
mixins.CreateModelMixin	    create   POST	  创建数据
mixins.RetrieveModelMixin	retrieve GET	  检索数据
mixins.UpdateModelMixin	    update   PUT	  更新数据   perform_update PATCH 局部更新数据
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

    def need_auth_list_check(self, auth_name):
        # 只需登录白名单
        if auth_name in ['userinfo', 'export*', ]:
            return True
        else:
            return False

    def has_permission(self, request, view):
        # 动态权限层 后期拆分 这里只验证动态权限
        # print('请求的path：', request.path)
        # print('请求的path拆分：', request.path.split('/')[1])
        auth_name = request.path.split('/')[1]
        # 无用户登录时
        if not bool(request.auth):
            return False
        # 当是超级管理员时
        if request.user.group.group_type == 'SuperAdmin':
            return True
        # 访问只需登录路由时
        if self.need_auth_list_check(auth_name):
            return True
        admin_auth = AuthPermission.objects.filter(object_name=auth_name, auth_id=request.user.auth_id).first()
        if request.user.group.group_type in ['SuperAdmin', 'Admin'] and admin_auth:
            if view.action in ['list', 'retrieve']:
                # 查看权限
                return bool(admin_auth.auth_list == True)
            elif view.action == 'create':
                # 创建权限
                return bool(admin_auth.auth_create == True)
            elif view.action in ['update', 'partial_update']:
                # 修改权限
                return bool(admin_auth.auth_update == True)
            elif view.action == 'destroy':
                # 删除权限
                return bool(admin_auth.auth_destroy == True)
            else:
                return False
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)