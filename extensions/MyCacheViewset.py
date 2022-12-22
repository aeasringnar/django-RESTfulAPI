from rest_framework.viewsets import ModelViewSet
from extensions.MyCache import RedisCacheForDecoratorV1


class MyModelViewSet(ModelViewSet):
    is_public = True
    
    @RedisCacheForDecoratorV1('r', 5*60)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @RedisCacheForDecoratorV1('w', 5*60)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @RedisCacheForDecoratorV1('w', 5*60)
    def partial_update(self, serializer):
        return super().partial_update(serializer)
    
    @RedisCacheForDecoratorV1('w', 5*60)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @RedisCacheForDecoratorV1('w', 5*60)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)