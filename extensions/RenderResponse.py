from rest_framework.renderers import JSONRenderer


class BaseJsonRenderer(JSONRenderer):
    '''
    重构render方法，定制DRF返回的response格式
    '''
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            if isinstance(data, dict) and 'msg' in data and 'code' in data: return super().render(data, accepted_media_type, renderer_context)
            ret = {
                'msg': 'ok',
                'code': 0,
                'data': data,
            }
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)