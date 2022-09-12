import jwt
import logging
from typing import *
from datetime import datetime
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError
from django.db.models import Model


class JwtToken:
    
    def __init__(self) -> None:
        self.key = settings.JWT_SETTINGS['SIGNING_KEY']
        self.algrithms = settings.JWT_SETTINGS['ALGORITHMS']
        self.algrithm = settings.JWT_SETTINGS['ALGORITHMS'][0]
        self.header_type = settings.JWT_SETTINGS['AUTH_HEADER_TYPES']
        self.header_name = settings.JWT_SETTINGS['AUTH_HEADER_NAME']
        self.options = {
            'verify_signature': settings.JWT_SETTINGS['VERIFY_SIGNATURE'],
            'verify_exp': settings.JWT_SETTINGS['VERIFY_EXP'],
            'require': settings.JWT_SETTINGS['REQUIRE'],
        }
        # 对于自建的，这个没什么意义
        # self.audience = settings.JWT_SETTINGS['AUDIENCE']
        # self.issuer = settings.JWT_SETTINGS['ISSUER']
        # self.leeway = settings.JWT_SETTINGS['LEEWAY']
    
    def encode(self, payload: dict) -> str:
        '''将目标信息转为jwt的值'''
        tmp = {
            'exp': datetime.utcnow() + settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME']
        }
        payload.update(tmp)
        return jwt.encode(payload=payload, key=self.key, algorithm=self.algrithm)
    
    def decode(self, s: str) -> tuple:
        '''将jwt的值，也就是token转为目标对象'''
        try:
            res = jwt.decode(
                jwt=s,
                key=self.key,
                algorithms=self.algrithms,
                options=self.options
            )
            return res, ''
        except ExpiredSignatureError as e:
            return None, 'Token expired.'
        except InvalidSignatureError as e:
            return None, 'Token is not valid.'
        except DecodeError as e:
            return None, 'Not enough segments.'
    
    def encode_user(self, payload: dict) -> str:
        '''将输入的payload，主要是要加密的数据，转为jwt的token字符串'''
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dict type.")
        if 'id' not in payload or 'jwt_version' not in payload:
            raise KeyError("Payload must contain the 'id' and 'jwt_ersion' fields.")
        return self.encode(payload)
    
    def decode_user(self, s: str, User: Model) -> tuple:
        '''将传入的jwt的token值转为内置的User对象'''
        try:
            obj, msg = self.decode(s)
            if not obj: return obj, msg
            user = User.objects.values("id", "jwt_version", "is_freeze").filter(id=obj["id"]).first()
            if not user: return None, "The account does not exist."
            if user.get("jwt_version") != obj["jwt_version"]: return None, "The token has been refreshed."
            if user.get("is_freeze"): return None, "The account was frozen."
            return User.objects.filter(id=obj["id"]).first(), ""
        except Exception as e:
            logging.error(f"将jwt解析为用户时发生异常：{e}")
            logging.exception(e)
            return None, str(e)
    
    def check_headers_jwt(self, target: str) -> tuple:
        '''检查请求头中的jwt'''
        target_ls = target.strip().split(" ")
        if len(target_ls) != 2: return None, "Invalid Authorization header. No credentials provided. Need 'Bearer <token value>'."
        header_type, value = target_ls
        if header_type != self.header_type: return None, "The message header is invalid, need 'Bearer <token value>'."
        return value, ""