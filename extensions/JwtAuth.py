from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from extensions.JwtToken import JwtToken
from apps.user.models import User


class JwtAuthentication(BaseAuthentication):
    www_authenticate_realm = 'api'
    
    def __init__(self) -> None:
        super().__init__()
        self.jwt = JwtToken()
    
    def authenticate(self, request):
        token = request.META.get(self.jwt.header_name, '')
        if not token:
            return None
        token, msg = self.jwt.check_headers_jwt(token)
        if not token:
            raise AuthenticationFailed(msg)
        user, msg = self.jwt.decode_user(token, User)
        if not user:
            raise AuthenticationFailed(msg)
        return user, token
    
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(self.jwt.header_type, self.www_authenticate_realm)