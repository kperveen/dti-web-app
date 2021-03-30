from django.urls import path
from . import views
from .views import index, download_file

urlpatterns = [path('', views.index, name='index'),path('download_file', views.download_file, name='download_file')]
