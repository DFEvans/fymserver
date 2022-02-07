from django.db import models

from fymserver.storage_backends import MapDataS3Storage


# Create your models here.
class Map(models.Model):
    id = models.IntegerField(primary_key=True)
    modified_date = models.DateField()
    jpg_file = models.FileField(storage=MapDataS3Storage())
    yrd_file = models.FileField(storage=MapDataS3Storage())
    his_file = models.FileField(storage=MapDataS3Storage())
