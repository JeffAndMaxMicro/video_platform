from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from ..models import Comment
from ..models import Video
from ..serializers import CommentListSerializer, CommentDetailSerializer, CommentSerializer
import redis
from videoPlateform import settings
from django.utils import timezone


redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        video_id = self.kwargs['video_pk']
        video = get_object_or_404(Video, pk=video_id)
        serializer.save(
            video=video,
            user_id=self.request.user.id,  # 假設你使用的是 Django 的默認 User 模型
            timestamp=timezone.now()
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CommentListSerializer
        elif self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentSerializer