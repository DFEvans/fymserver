from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MapDataS3Storage(S3Boto3Storage):
    bucket_name = "fymserver-mapfiles"
    location = "private"
    default_acl = "private"
    file_overwrite = False
    custom_domain = False
