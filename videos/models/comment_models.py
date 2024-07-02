from django.db import models

from .video_models import Video
from .user_models import User

from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField


class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # 自動設置創建時間
    updated_at = models.DateTimeField(auto_now=True)  # 自動設置更新時間
    reply_to = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        managed = True

class MongoDBComment(Document):
    video_id = StringField(required=True)
    comment_id = StringField(required=True, unique=True)  # 与 MySQL 中的评论ID对应
    content = StringField(required=True)
    replies = ListField(ReferenceField('self')) # 回覆列表，可以为空
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        'collection': 'comments_content'
    }