from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from .utils import jwt_get_user_id_from_payload_handler, jwt_decode_handler
from user.models import User
from .settings import api_settings


class JWTAuthentication(BaseAuthentication):
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = 'Token过期'
            raise exceptions.AuthenticationFailed({"message": msg,"errorCode":1,"data":{}})
        except jwt.DecodeError:
            msg = 'Token不合法'
            raise exceptions.AuthenticationFailed({"message": msg,"errorCode":1,"data":{}})
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)
        return user, jwt_value

    def authenticate_credentials(self, payload):
        id = jwt_get_user_id_from_payload_handler(payload)
        if not id:
            raise exceptions.AuthenticationFailed({"message": "没有该用户","errorCode":1,"data":{}})
        try:
            user = User.objects.filter(id=id).first()
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed({"message": "没有该用户","errorCode":1,"data":{}})
        return user

    def get_jwt_value(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '').split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth or auth[0].lower() != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = 'Invalid Authorization header. No credentials provided.'
            raise exceptions.AuthenticationFailed({"message": "消息头不合法","errorCode":1,"data":{}})
        elif len(auth) > 2:
            msg = 'Invalid Authorization header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed({"message": "消息头不合法","errorCode":1,"data":{}})

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)
