from datetime import date

from django.db import models

from fymserver.storage_backends import TrainDataS3Storage
from players.models import Player


class TrainState(models.IntegerChoices):
    AVAILABLE = 1
    DOWNLOADED = 2


class Train(models.Model):
    train_file = models.FileField(storage=TrainDataS3Storage())
    from_player = models.CharField(max_length=40)
    to_player = models.CharField(max_length=40)
    downloaded_by = models.ForeignKey(
        "players.Player", on_delete=models.RESTRICT, null=True
    )
    upload_date = models.DateField(default=date.today)
    state = models.IntegerField(
        choices=TrainState.choices, default=TrainState.AVAILABLE
    )

    def set_downloaded(self, player: Player) -> None:
        self.state = TrainState.DOWNLOADED
        self.downloaded_by = player
