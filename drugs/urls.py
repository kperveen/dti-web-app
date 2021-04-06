from django.urls import path
from . import views, results, about
from .views import index, download_file
urlpatterns = [path('', views.index, name='index')]

urlpatterns += [
    path('results/', results.index, name="results"),
    path('about/', about.index, name="about"),
    path('download_file', views.download_file, name='download_file')
]