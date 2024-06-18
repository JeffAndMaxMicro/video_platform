import os
import pika
import json
from django.core.management.base import BaseCommand
from videos.models import Video
from videoPlateform import settings

class Command(BaseCommand):
    help = 'Starts the RabbitMQ worker for processing video upload events.'

    def handle(self, *args, **kwargs):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT))
        channel = connection.channel()
        
        # 創建Exchange
        channel.exchange_declare(exchange='video_exchange', exchange_type='direct', durable=True)
        
        # 創建並綁定隊列
        channel.queue_declare(queue='video_queue', durable=True)
        channel.queue_bind(exchange='video_exchange', queue='video_queue', routing_key='video_key')
        
        channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            video_data = json.loads(body)
            self.save_video_metadata_to_db(video_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue='video_queue', on_message_callback=callback)
        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def save_video_metadata_to_db(self, video_data):
        video = Video(
            video_id=video_data['video_id'],
            file_path=video_data['file_path'],
            bucket_name=video_data['bucket_name'],
            object_name=video_data['object_name']
        )
        video.save()
        print("Video metadata saved successfully.")