# Generated by Django 4.0.2 on 2022-02-09 22:06

from django.db import migrations, models
import fymserver.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='his_file',
            field=models.FileField(storage=fymserver.storage_backends.MapDataS3Storage(), upload_to=''),
        ),
        migrations.AlterField(
            model_name='map',
            name='jpg_file',
            field=models.FileField(storage=fymserver.storage_backends.MapDataS3Storage(), upload_to=''),
        ),
        migrations.AlterField(
            model_name='map',
            name='yrd_file',
            field=models.FileField(storage=fymserver.storage_backends.MapDataS3Storage(), upload_to=''),
        ),
    ]
