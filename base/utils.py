import base64, json, re, jwt
from datetime import datetime
from calendar import timegm
from .settings import api_settings
# 导入谷歌验证码相关模块
import pyotp,time
# 导入使用缓存的模块
from django.core.cache import cache

def jwt_payload_handler(account):
    payload = {
        'id': account.pk,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA  # 过期时间
    }

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


def jwt_get_user_id_from_payload_handler(payload):
    return payload.get('id')


# def jwt_get_phone_from_payload_handler(payload):
#     return payload.get('phone')


def jwt_encode_handler(payload):
    return jwt.encode(
        payload,
        api_settings.JWT_PRIVATE_KEY or api_settings.JWT_SECRET_KEY,
        api_settings.JWT_ALGORITHM
    ).decode('utf-8')


def jwt_decode_handler(token):
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }

    return jwt.decode(
        token,
        api_settings.JWT_PUBLIC_KEY or api_settings.JWT_SECRET_KEY,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM]
    )


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token
    }

# google验证模块，必须设置对应的key，才可以操作
def google_otp(pin):
    nowtime = int(time.time())
    totp = pyotp.TOTP(api_settings.GOOGLE_AUTH_ADMIN)
    #totp.verify(pin, nowtime, 5)
    return totp.verify(pin, nowtime, 5)

# 打印请求体的方法
def request_log(request):
    print('====================================request body信息==================================================')
    print('body信息：',request.data)
    print('URL参数：',request.GET)
    print('==================================View视图函数内部信息================================================')
