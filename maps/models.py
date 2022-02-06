from django.db import models


# Create your models here.
class Map(models.Model):
    id = models.IntegerField(primary_key=True)
    modified_date = models.DateField()
    jpg_file = models.FileField()
    yrd_file = models.FileField()
    his_file = models.FileField()
