from django.conf.urls import url
from apps.authenticate.actions import LogoutAction, VKCallBack, VKAuthAction, LoginAction


urlpatterns = [
    url(r'^logout$', LogoutAction.as_view(), name='logout'),
    url(r'^login$', LoginAction.as_view(), name='login'),
    url(r'^vk_login$', VKAuthAction.as_view(), name='vk_login'),
    url(r'^vk/login/callback/', VKCallBack.as_view(), name='vkcallback'),
]
