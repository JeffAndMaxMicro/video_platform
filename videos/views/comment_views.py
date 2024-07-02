from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from ..models import Comment
from ..models import Video
from ..serializers import CommentListSerializer, CommentDetailSerializer, CommentSerializer
from videoPlateform import settings
from django.utils import timezone

from videoPlateform import mongo_global_init
# import redis
# mongo_global_init()
# redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

import pika
import json
from videoPlateform import settings

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        video_id = self.kwargs['video_pk']
        video = get_object_or_404(Video, pk=video_id)
        user_id=self.request.user.id

        # 从请求数据中获取reply_to_comment_id，如果有的话
        reply_to_comment_id = self.request.data.get('reply_to_comment_id')

        # 连接到RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT))
        channel = connection.channel()

        # 声明交换机
        channel.exchange_declare(exchange='comment_exchange', exchange_type='direct', durable=True)

        # 声明队列并绑定到交换机
        channel.queue_declare(queue='comment_queue', durable=True)
        channel.queue_bind(exchange='comment_exchange', queue='comment_queue', routing_key='comment_key')

        # 構建要發送到 RabbitMQ 的消息
        comment_data = {
            'video_id': video_id,
            'user_id': user_id,
            'content': self.request.data['content'],
        }

        # 如果有reply_to_comment_id，则添加到消息中
        if reply_to_comment_id:
            comment_data['reply_to_comment_id'] = reply_to_comment_id

        # 发送消息到交换机
        channel.basic_publish(
            exchange='comment_exchange',
            routing_key='comment_key',
            body=json.dumps(comment_data),
            properties=pika.BasicProperties(delivery_mode=2)  # 使消息持久化
        )

        # 关闭连接
        connection.close()

    def get_serializer_class(self):
        if self.action == 'list':
            return CommentListSerializer
        elif self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentSerializer