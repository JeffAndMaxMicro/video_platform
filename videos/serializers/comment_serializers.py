from rest_framework import serializers
from .video_serializers import VideoSerializer
from ..models import Comment

class CommentSerializer(serializers.ModelSerializer):
    reply_to_comment_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['id', 'video_id', 'user_id', 'content', 'created_at', 'updated_at', 'reply_to_comment_id']
        read_only_fields = ['user_id', 'created_at', 'updated_at' 'id', 'video_id']

    def create(self, validated_data):
        reply_to_comment_id = validated_data.pop('reply_to_comment_id', None)
        if reply_to_comment_id:
            try:
                reply_to_comment = Comment.objects.get(id=reply_to_comment_id)
                validated_data['reply_to'] = reply_to_comment
            except Comment.DoesNotExist:
                raise serializers.ValidationError("Reply to comment not found.")
        return super().create(validated_data)

class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'created_at', 'updated_at' 'id', 'id', 'video_id']

class CommentDetailSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'video', 'user_id', 'content', 'created_at', 'updated_at', 'replies']

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentListSerializer(replies, many=True).data

    def get_video(self, obj):
        return VideoSerializer(obj.video).data