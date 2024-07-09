import json
import pika
import redis
import logging
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from videos.models import Video, Comment, MongoDBComment
from videoPlateform.mongo_setup import mongo_global_init

User = get_user_model()

class Command(BaseCommand):
    help = 'Starts the RabbitMQ worker for processing comment events.'

    def handle(self, *args, **kwargs):
        # 初始化 MongoDB 連接
        mongo_global_init()

        # 初始化 Redis 客戶端
        redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT))
        channel = connection.channel()

        # 創建Exchange
        channel.exchange_declare(exchange='comment_exchange', exchange_type='direct', durable=True)

        # 創建並綁定隊列
        channel.queue_declare(queue='comment_queue', durable=True)
        channel.queue_bind(exchange='comment_exchange', queue='comment_queue', routing_key='comment_key')

        channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            comment_data = json.loads(body)
            try:
                self.save_comment_to_databases(comment_data, redis_client)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                # 選擇重新排隊消息或丟棄
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume(queue='comment_queue', on_message_callback=callback)
        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def save_comment_to_databases(self, comment_data, redis_client):
        try:
            # 保存到 MySQL
            video = Video.objects.get(pk=comment_data['video_id'])
            user = User.objects.get(id=comment_data['user_id'])

            # 获取reply_to_comment，如果有的话
            reply_to_comment = None
            if 'reply_to_comment_id' in comment_data:
                try:
                    reply_to_comment = Comment.objects.get(id=comment_data['reply_to_comment_id'])
                except Comment.DoesNotExist:
                    logging.error(f"Reply to comment with id {comment_data['reply_to_comment_id']} not found.")
                    raise

            comment = Comment.objects.create(
                video=video,
                user=user,
                content=comment_data['content'],
                reply_to=reply_to_comment  # 設置 reply_to 字段
            )
            print(f"Comment for video {video.title} saved to MySQL successfully.")
        except Exception as e:
            logging.error(f"Error saving comment to MySQL: {e}")
            raise

        try:
            # 保存到 MongoDB
            mongo_comment = MongoDBComment(
                video_id=str(comment.video.id),
                comment_id=str(comment.id),  # 与 MySQL 中的评论ID对应
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                # replies=[]
            )
            # if reply_to_comment:
            #     mongo_comment.replies.append(reply_to_comment.id)  # 添加回覆的ID
            mongo_comment.save()
            print(f"Comment for video {video.title} saved to MongoDB successfully.")
        except Exception as e:
            logging.error(f"Error saving comment to MongoDB: {e}")
            # 補償：刪除已保存的 MySQL 記錄
            Comment.objects.filter(pk=comment.id).delete()
            raise

        # 保存到 Redis
        redis_comment_key = f"video:{comment_data['video_id']}:comments"
        redis_client.delete(redis_comment_key)
        print(f"Comment for video {video.title} saved successfully and cache expired.")
