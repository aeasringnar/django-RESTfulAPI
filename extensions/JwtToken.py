from django.conf import settings
from typing import *
import logging
from datetime import datetime
import jwt


class JwtToken:
    
    def __init__(self) -> None:
        self.key = settings.JWT_SETTINGS['SIGNING_KEY']
        self.algrithms = settings.JWT_SETTINGS['ALGORITHMS']
        self.options = {
            'verify_signature': settings.JWT_SETTINGS['VERIFY_SIGNATURE'],
            'verify_exp': settings.JWT_SETTINGS['VERIFY_EXP'],
            'require': settings.JWT_SETTINGS['REQUIRE'],
        }
        # 对于自建的，这个没什么意义
        # self.audience = settings.JWT_SETTINGS['AUDIENCE']
        # self.issuer = settings.JWT_SETTINGS['ISSUER']
        # self.leeway = settings.JWT_SETTINGS['LEEWAY']
    
    def encode(self, obj: dict) -> str:
        payload = {
            'exp': datetime.now() + settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME']
        }
        obj.update(payload)
        return jwt.encode(payload=payload, key=self.key, algorithm=self.algrithms)
    
    def decode(self, s: str) -> tuple:
        res = jwt.decode(
            jwt=s,
            key=self.key,
            algorithms=self.algrithms,
            options=self.options
        )
        return res