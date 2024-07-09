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
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', read_only=True)
    replies = serializers.SerializerMethodField()
    mongo_id = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'content', 'created_at', 'updated_at', 'replies', 'mongo_id']
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'id', 'video_id', 'replies', 'mongo_id']

    def get_replies(self, obj):
        if hasattr(obj, 'nested_replies'):
            return CommentListSerializer(obj.nested_replies, many=True).data
        return []
    
    def get_mongo_id(self, obj):
        if hasattr(obj, 'mongo_id'):
            return obj.mongo_id
        return None

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