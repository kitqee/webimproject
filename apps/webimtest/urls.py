from django.conf.urls import url
from apps.webimtest.actions import IndexAction

urlpatterns = [
    url(r'^$', IndexAction.as_view(), name='index'),
]

