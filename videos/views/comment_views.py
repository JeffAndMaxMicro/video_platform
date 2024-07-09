import datetime
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Comment, MongoDBComment
from ..models import Video
from ..serializers import CommentListSerializer, CommentDetailSerializer, CommentSerializer
from videoPlateform import settings
from django.utils import timezone
from bson import json_util
from videoPlateform import mongo_global_init
import redis
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

    def list(self, request, *args, **kwargs):
        video_id = self.kwargs['video_pk']
        
        redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        redis_comment_key = f"video:{video_id}:comments"

        cached_comments = redis_client.get(redis_comment_key)
        if cached_comments:
            return Response(json.loads(cached_comments))

        mysql_comments = self.filter_queryset(self.get_queryset().filter(video_id=video_id))

        mongo_global_init()
        mongo_comments = MongoDBComment.objects.filter(video_id=str(video_id)).only(
            'comment_id', 'content'
        )
        mongo_comments_dicts = [mongo_comment.to_mongo().to_dict() for mongo_comment in mongo_comments]

        comments_dict = {str(comment.id): comment for comment in mysql_comments}

        for mongo_comment in mongo_comments_dicts:
            comment_id = str(mongo_comment['comment_id'])
            if comment_id in comments_dict:
                comments_dict[comment_id].mongo_id = str(mongo_comment['_id'])

        def build_nested_comments(comments_dict):
            nested_comments = []
            for comment_id, comment in comments_dict.items():                    
                if comment.reply_to_id:
                    parent_comment = comments_dict.get(str(comment.reply_to_id))
                    if parent_comment:
                        if not hasattr(parent_comment, 'nested_replies'):
                            setattr(parent_comment, 'nested_replies', [])
                            parent_comment.nested_replies.append(comment)
                else:
                    nested_comments.append(comment)
            return nested_comments

        nested_comments = build_nested_comments(comments_dict)

        # 使用 CommentListSerializer 來序列化數據
        serializer = self.get_serializer_class()(nested_comments, many=True)
        serialized_data = serializer.data

        redis_client.set(redis_comment_key, json.dumps(serialized_data, default=json_util.default), ex=3600)

        return Response(serialized_data)

    def get_serializer_class(self):
        if self.action == 'list':
            return CommentListSerializer
        elif self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentSerializer