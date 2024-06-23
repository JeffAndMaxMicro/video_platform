from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import VideoViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'', VideoViewSet)

# 創建嵌套路由
videos_router = NestedDefaultRouter(router, r'', lookup='video')
videos_router.register(r'comments', CommentViewSet, basename='video-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(videos_router.urls)),
]