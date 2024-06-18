import json
from django.http import JsonResponse
import pika
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from videoPlateform import settings
from .models import Video
from .serializers import VideoSerializer

from rest_framework.response import Response
from rest_framework import status
from minio import Minio

from django.views.decorators.csrf import csrf_exempt

import hashlib
import uuid

def generate_random_hash():
    return hashlib.md5(uuid.uuid4().hex.encode()).hexdigest()

@api_view(['POST'])
@csrf_exempt
def VideoUpload(request):
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

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT))
        channel = connection.channel()
        channel.queue_declare(queue='video_queue', durable=True)

        channel.basic_publish(
            exchange='video_exchange',
            routing_key='video_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # 使消息持久化
        )

        connection.close()
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def VideoList(request):
    videos = Video.objects.all()
    serializer = VideoSerializer(videos, many=True)
    return JsonResponse(serializer.data, safe=False)
