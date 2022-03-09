import uuid

from django.db import models


# Create your models here.
class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=40)

    def __str__(self):
        return f"Player ({self.username})"
