from unittest import mock

from django.core.files import File
from django.test import TestCase
from override_storage import override_storage
from override_storage.storage import LocMemStorage

from .models import Train


def mock_file(filename: str) -> mock.MagicMock:
    mock_file = mock.MagicMock(spec=File, name="MockFile")
    mock_file.name = filename
    mock_file.size = 1
    return mock_file


@override_storage()
class TrainModelTests(TestCase):
    def test_train_file_is_stored(self):
        train = Train.objects.create(train_file=mock_file("train01.zrn"))
        self.assertEqual("train01.zrn", train.train_file.name)
