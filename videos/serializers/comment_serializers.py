from rest_framework import serializers
from .video_serializers import VideoSerializer
from ..models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'video_id', 'user_id', 'comment', 'timestamp']
        read_only_fields = ['user_id', 'timestamp', 'id', 'video_id']

class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'comment', 'timestamp']
        read_only_fields = ['user_id', 'timestamp', 'id', 'video_id']

class CommentDetailSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'video', 'user_id', 'comment', 'timestamp']

    def get_video(self, obj):
        return VideoSerializer(obj.video).data