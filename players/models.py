import random
import string
import uuid

from django.db import models


def generate_token() -> str:
    return "".join(
        random.SystemRandom().choices(string.ascii_letters + string.digits, k=128)
    )


# Create your models here.
class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=40)
    email = models.CharField(max_length=200)
    token = models.CharField(max_length=128, default=generate_token)

    def __str__(self):
        return f"Player ({self.username})"

    def validate_token(self, token: str) -> bool:
        return token == self.token
