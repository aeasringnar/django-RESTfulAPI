from django.conf import settings
import datetime
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'JWT_AUTH', None)

DEFAULTS = {
    'JWT_PRIVATE_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_SECRET_KEY': settings.SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=21),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=21),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',

    'PAGE_SIZE': 20,
    # 'ORDER_PAGE_SIZE':5,
    # 'MAX_FILE_UPLOAD_SIZE': 12 * 1000 * 1000,
    # 'GOOGLE_AUTH_ADMIN': "ME4WGNBWGI4GMNLC",
    # 'ZOOM_API_KEY': 'rhfF2x-qRj2QbWNWC5s75w',
    # 'ZOOM_API_SECRET': 'SA7qSdBAwu4MgxEKcYxDrPtdBeoQMtNwWTwN',
    # 'YP_APIKEY': '7be50ac81074413e4d7f6b08fd19eb7e',
    # 'GOOGLE_AUTH_MEMBER': "ME4WGNBWGI4GMNLC",
    # 'GOOGLE_AUTH_MERCHANT': "HAZTMZJRHFSDKODE",
    # 'GOOGLE_AUTH_DAIMAI':"XSBB2PZPRUXINTVA",
    # 'GOOGLE_AUTH_RIDER': "HE2DMNJZMNTDINZX",

}

api_settings = APISettings(USER_SETTINGS, DEFAULTS)