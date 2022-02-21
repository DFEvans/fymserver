from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MapDataS3Storage(S3Boto3Storage):
    bucket_name = "freightyardmanager-serverdata"
    location = "maps"
    default_acl = "private"
    file_overwrite = True
    custom_domain = False


class TrainDataS3Storage(S3Boto3Storage):
    bucket_name = "freightyardmanager-serverdata"
    location = "trains"
    default_acl = "private"
    file_overwrite = True
    custom_domain = False
