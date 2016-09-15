"""weather_maniac URL Configuration"""

from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.render_index, name='index'),
    url(r'^statistics$', views.render_statistics, name='statistics'),
    url(r'^prediction$', views.render_prediction, name='prediction'),
    url(r'^graph$', views.render_graph, name='graph'),
    url(r'^json$', views.return_json, name='json')
]
