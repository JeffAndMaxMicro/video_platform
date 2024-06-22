from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, CommentViewSet

# 創建一個DefaultRouter實例並註冊ViewSet
router = DefaultRouter()
router.register(r'', VideoViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),  # 包含所有由DefaultRouter生成的路由
]