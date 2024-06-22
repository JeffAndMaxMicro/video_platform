from django.db import models
from .user_models import User

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    video_hash = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'videos'