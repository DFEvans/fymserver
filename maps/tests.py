from unittest import mock

from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Map


def mock_file(filename: str) -> mock.MagicMock:
    mock_file = mock.MagicMock(spec=File, name="MockFile")
    mock_file.name = filename
    return mock_file


# Create your tests here.
class MapsIndexViewTests(TestCase):
    def test_works(self):
        response = self.client.get(reverse("maps:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world!")


class MapModelTests(TestCase):
    def test_map_id_1001_should_be_valid(self):
        map = Map(id=1001)
        self.assertEqual(1001, map.id)

    def test_modified_date_is_stored(self):
        mod_date = timezone.datetime(2020, 1, 1, 0, 0, 0)
        map = Map(modified_date=mod_date)
        self.assertEqual(mod_date, map.modified_date)

    def test_jpg_file_is_stored(self):
        jpg_file = mock_file("1001.jpg")
        map = Map(jpg_file=jpg_file)
        self.assertEqual("1001.jpg", map.jpg_file.name)

    def test_yrd_file_is_stored(self):
        yrd_file = mock_file("1001.yrd")
        map = Map(yrd_file=yrd_file)
        self.assertEqual("1001.yrd", map.yrd_file.name)

    def test_his_file_is_stored(self):
        his_file = mock_file("1001.his")
        map = Map(his_file=his_file)
        self.assertEqual("1001.his", map.his_file.name)
