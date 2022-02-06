from django.db import models


# Create your models here.
class Map(models.Model):
    map_id = models.IntegerField()
    modified_date = models.DateField()
