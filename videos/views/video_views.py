from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ..models import Video
from ..serializers import VideoSerializer

import hashlib
import uuid

import pika
from minio import Minio
import json
from videoPlateform import settings

def generate_random_hash():
    return hashlib.md5(uuid.uuid4().hex.encode()).hexdigest()

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    @method_decorator(csrf_exempt)
    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('video_file')
        # 检查文件是否为空
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False  # 如果你的 MinIO 未启用 TLS，请设置为 False
        )

        file_hash = generate_random_hash()

        # 将文件上传到 MinIO
        try:
            minio_client.put_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=file_hash,
                data=file_obj,
                length=file_obj.size,
                content_type='video/mp4'  # 根据实际文件类型设置
            )

            message = {
                'title': request.data.get('title'),
                'description': request.data.get('description'),
                'video_hash': file_hash,
                'user_id': request.user.id,
            }

            # 连接到RabbitMQ
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT))
            channel = connection.channel()

            # 声明交换机
            channel.exchange_declare(exchange='video_exchange', exchange_type='direct', durable=True)

            # 声明队列并绑定到交换机
            channel.queue_declare(queue='video_queue', durable=True)
            channel.queue_bind(exchange='video_exchange', queue='video_queue', routing_key='video_key')

            # 发送消息到交换机
            channel.basic_publish(
                exchange='video_exchange',
                routing_key='video_key',
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)  # 使消息持久化
            )

            # 关闭连接
            connection.close()
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def list_videos(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)