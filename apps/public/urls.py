from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
# Create your views here.

# router.register(r'yourpath', YourViewSet, basename="ViewSetPath")
# urlpatterns = [
#     path('', include(router.urls)),
#     path('yourpath/', YourView.as_view(), name='ViewPath'),
# ]