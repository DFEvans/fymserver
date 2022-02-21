from django.db import models

from fymserver.storage_backends import TrainDataS3Storage


class Train(models.Model):
    train_file = models.FileField(storage=TrainDataS3Storage())
