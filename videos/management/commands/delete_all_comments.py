from django.core.management.base import BaseCommand
from videos.models import MongoDBComment, Comment
from videoPlateform.mongo_setup import mongo_global_init

class Command(BaseCommand):
    help = 'Delete all comments from MySQL and MongoDB'

    def handle(self, *args, **kwargs):
        # 刪除 MySQL 中的評論
        Comment.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all comments from MySQL'))

        mongo_global_init()
        # 刪除 MongoDB 中的評論
        MongoDBComment.objects.delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all comments from MongoDB'))