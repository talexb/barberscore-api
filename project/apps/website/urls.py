from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^collection/$', views.collections, name='collections'),
    url(r'^collection/(?P<id>[a-zA-Z0-9-]+)/$', views.collection, name='collection'),
    url(r'^merge/(?P<id>[a-zA-Z0-9-]+)/$', views.merge, name='merge'),
    url(r'^skip/(?P<id>[a-zA-Z0-9-]+)/$', views.skip, name='skip'),
    url(r'^flag/(?P<id>[a-zA-Z0-9-]+)/$', views.flag, name='flag'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)