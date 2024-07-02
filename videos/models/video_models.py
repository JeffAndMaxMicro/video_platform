from django.db import models
from .user_models import User

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    video_hash = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # 自動設置創建時間
    updated_at = models.DateTimeField(auto_now=True)  # 自動設置更新時間

    class Meta:
        managed = True
        db_table = 'videos'