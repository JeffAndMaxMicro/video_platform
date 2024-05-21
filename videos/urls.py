from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.VideoUpload, name='video-upload'),
    path('', views.VideoList, name='video-list'),
]