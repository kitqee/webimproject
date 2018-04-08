from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^auth/', include('apps.authenticate.urls')),
    url(r'^', include('apps.webimtest.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
