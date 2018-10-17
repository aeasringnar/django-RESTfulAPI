from django.conf.urls import url
from base import views

urlpatterns = [
    url(r'^login',views.Login.as_view(),name='login'),
    # url(r'^register',views.Register.as_view(),name='register'),
    # url(r'^userinfo',views.UserInfo.as_view(),name='userinfo'),
]