from rest_framework.renderers import JSONRenderer


class BaseJsonRenderer(JSONRenderer):
    '''
    重构render方法，定制DRF返回的response格式
    '''
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # print(renderer_context["response"].status_code)
        if renderer_context:
            if isinstance(data, dict) and data.get('message'): return super().render(data, accepted_media_type, renderer_context)
            ret = {
                'message': 'ok',
                'errorCode': 0,
                'data': data,
            }
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)