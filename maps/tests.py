from typing import cast
from unittest import mock

from django.core.files import File
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from override_storage import override_storage

from .models import Map


def mock_file(filename: str) -> mock.MagicMock:
    mock_file = mock.MagicMock(spec=File, name="MockFile")
    mock_file.name = filename
    mock_file.size = 1
    return mock_file


def create_map(map_id=1001, mod_date=None, jpg_file=None, yrd_file=None, his_file=None):
    if not mod_date:
        mod_date = timezone.now()

    jpg_file = jpg_file or mock_file(f"{map_id}.jpg")
    yrd_file = yrd_file or mock_file(f"{map_id}.yrd")
    his_file = his_file or mock_file(f"{map_id}.his")

    return Map.objects.create(
        id=map_id,
        modified_date=mod_date,
        jpg_file=jpg_file,
        yrd_file=yrd_file,
        his_file=his_file,
    )


@override_storage()
class MapModelTests(TestCase):
    def test_map_id_1001_should_be_valid(self):
        map = create_map(map_id=1001)
        self.assertEqual(1001, map.id)

    def test_modified_date_is_stored(self):
        mod_date = timezone.datetime(2020, 1, 1, 0, 0, 0)
        map = create_map(mod_date=mod_date)
        self.assertEqual(mod_date, map.modified_date)

    def test_jpg_file_is_stored(self):
        jpg_file = mock_file("1001.jpg")
        map = create_map(jpg_file=jpg_file)
        self.assertEqual("1001.jpg", map.jpg_file.name)

    def test_yrd_file_is_stored(self):
        yrd_file = mock_file("1001.yrd")
        map = create_map(yrd_file=yrd_file)
        self.assertEqual("1001.yrd", map.yrd_file.name)

    def test_his_file_is_stored(self):
        his_file = mock_file("1001.his")
        map = create_map(his_file=his_file)
        self.assertEqual("1001.his", map.his_file.name)


@override_storage()
class MapJpgFileViewTests(TestCase):
    def test_jpg_view_redirects_to_file(self):
        map = create_map()
        url = reverse("maps:jpg_file", args=(map.id,))
        response = self.client.get(url)
        self.assertRedirects(response, "/1001.jpg", fetch_redirect_response=False)


@override_storage()
class MapYrdFileViewTests(TestCase):
    def test_yrd_view_redirects_to_file(self):
        map = create_map()
        url = reverse("maps:yrd_file", args=(map.id,))
        response = self.client.get(url)
        self.assertRedirects(response, "/1001.yrd", fetch_redirect_response=False)


@override_storage()
class MapHisFileViewTests(TestCase):
    def test_his_view_redirects_to_file(self):
        map = create_map()
        url = reverse("maps:his_file", args=(map.id,))
        response = self.client.get(url)
        self.assertRedirects(response, "/1001.his", fetch_redirect_response=False)


@override_storage()
class MapModifiedDateViewTests(TestCase):
    def test_date_view_returns_json_blob(self):
        expected_json = {"modified_date": "2000-01-31"}

        map = create_map(mod_date=timezone.datetime(2000, 1, 31, 12, 34, 56))
        url = reverse("maps:modified_date", args=(map.id,))
        response = cast(JsonResponse, self.client.get(url))
        self.assertJSONEqual(response.content.decode(), expected_json)


@override_storage()
class MapListViewTests(TestCase):
    def test_returns_empty_list_for_no_maps(self):
        expected_json = {"maps": []}

        url = reverse("maps:index")
        response = self.client.get(url)
        self.assertJSONEqual(response.content.decode(), expected_json)

    def test_returns_single_entry_for_one_known_map(self):
        expected_json = {"maps": [1001]}

        create_map(map_id=1001)

        url = reverse("maps:index")
        response = self.client.get(url)
        self.assertJSONEqual(response.content.decode(), expected_json)

    def test_returns_multiple_maps_in_id_order(self):
        expected_json = {"maps": [1001, 1002]}

        create_map(map_id=1002)
        create_map(map_id=1001)

        url = reverse("maps:index")
        response = self.client.get(url)
        self.assertJSONEqual(response.content.decode(), expected_json)
