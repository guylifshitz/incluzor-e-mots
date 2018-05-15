
from django.urls import path
from django.urls import re_path
from django.urls import include, path
from . import views
from django.conf.urls import url
from django.urls import path
import mots

app_name = 'mots'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    path('<int:mot_id>/', views.detail, name='detail'),
    path('<int:pk>/edit', views.EditMot.as_view(), name='edit'),
]
