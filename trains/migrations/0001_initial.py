# Generated by Django 4.0.2 on 2022-02-21 20:50

import datetime

from django.db import migrations, models

import fymserver.storage_backends


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Train",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "train_file",
                    models.FileField(
                        storage=fymserver.storage_backends.TrainDataS3Storage(),
                        upload_to="",
                    ),
                ),
                ("from_player", models.CharField(max_length=40)),
                ("to_player", models.CharField(max_length=40)),
                ("downloaded_by", models.CharField(default="", max_length=40)),
                ("upload_date", models.DateField(default=datetime.date.today)),
                (
                    "state",
                    models.IntegerField(
                        choices=[(1, "Available"), (2, "Downloaded")], default=1
                    ),
                ),
            ],
        ),
    ]
