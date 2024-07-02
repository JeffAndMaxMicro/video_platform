# mongo_setup.py
from mongoengine import connect
from videoPlateform import settings

def mongo_global_init():
    connect(
        db=settings.MONGO_DB_NAME,
        host=f'mongodb://{settings.MONGO_HOSTS}',
        replicaset=settings.MONGO_REPLICAT_SET
    )