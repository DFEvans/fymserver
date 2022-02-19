from datetime import date
from io import BytesIO
from typing import cast
from unittest import mock

from django.core.files import File
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from override_storage import override_storage
from override_storage.storage import LocMemStorage

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


class OverwritingLocMemStorage(LocMemStorage):
    def get_available_name(self, name, max_length=None):
        if name in self.cache:
            del self.cache[name]
        return name


@override_storage(storage=OverwritingLocMemStorage)
class MapUpdateTests(TestCase):
    def assert_files_ok(
        self,
        map_id: int,
        mod_date: date,
        check_jpg: bool = True,
        check_yrd: bool = True,
        check_his: bool = True,
    ):
        assert Map.objects.filter(pk=map_id).exists()
        map_obj = cast(Map, Map.objects.get(pk=map_id))
        assert mod_date == map_obj.modified_date

        if check_jpg:
            assert f"{map_id}.jpg" == map_obj.jpg_file.name
            assert b"jpg_data" == map_obj.jpg_file.read()

        if check_yrd:
            assert f"{map_id}.yrd" == map_obj.yrd_file.name
            assert b"yrd_data" == map_obj.yrd_file.read()

        if check_his:
            assert f"{map_id}.his" == map_obj.his_file.name
            assert b"his_data" == map_obj.his_file.read()

    def test_update_succeeds_for_new_map(self):
        map_id = 1001
        modified_date = "2000-01-01"
        jpg_file = BytesIO(b"jpg_data")
        yrd_file = BytesIO(b"yrd_data")
        his_file = BytesIO(b"his_data")

        url = reverse("maps:update", args=(map_id,))
        self.client.post(
            url,
            {
                "jpg_file": jpg_file,
                "yrd_file": yrd_file,
                "his_file": his_file,
                "modified_date": modified_date,
            },
        )

        self.assert_files_ok(map_id, date(2000, 1, 1))

    def test_update_succeeds_for_existing_map(self):
        map_id = 1001
        modified_date = "2000-01-01"
        jpg_file = BytesIO(b"jpg_data")
        yrd_file = BytesIO(b"yrd_data")
        his_file = BytesIO(b"his_data")

        create_map(map_id)

        url = reverse("maps:update", args=(map_id,))
        self.client.post(
            url,
            {
                "jpg_file": jpg_file,
                "yrd_file": yrd_file,
                "his_file": his_file,
                "modified_date": modified_date,
            },
        )

        self.assert_files_ok(map_id, date(2000, 1, 1))

    def test_update_succeeds_for_jpg_only(self):
        map_id = 1001
        modified_date = "2000-01-01"
        jpg_file = BytesIO(b"jpg_data")

        create_map(map_id)

        url = reverse("maps:update", args=(map_id,))
        self.client.post(
            url,
            {
                "jpg_file": jpg_file,
                "modified_date": modified_date,
            },
        )

        self.assert_files_ok(map_id, date(2000, 1, 1), check_yrd=False, check_his=False)

    def test_update_succeeds_for_yrd_only(self):
        map_id = 1001
        modified_date = "2000-01-01"
        yrd_file = BytesIO(b"yrd_data")

        create_map(map_id)

        url = reverse("maps:update", args=(map_id,))
        self.client.post(
            url,
            {
                "yrd_file": yrd_file,
                "modified_date": modified_date,
            },
        )

        self.assert_files_ok(map_id, date(2000, 1, 1), check_jpg=False, check_his=False)

    def test_update_succeeds_for_his_only(self):
        map_id = 1001
        modified_date = "2000-01-01"
        his_file = BytesIO(b"his_data")

        create_map(map_id)

        url = reverse("maps:update", args=(map_id,))
        self.client.post(
            url,
            {
                "his_file": his_file,
                "modified_date": modified_date,
            },
        )

        self.assert_files_ok(map_id, date(2000, 1, 1), check_jpg=False, check_yrd=False)

    def test_update_succeeds_for_modified_date_only(self):
        map_id = 1001
        modified_date = "2000-01-01"

        create_map(map_id)

        url = reverse("maps:update", args=(map_id,))
        self.client.post(
            url,
            {
                "modified_date": modified_date,
            },
        )

        self.assert_files_ok(
            map_id, date(2000, 1, 1), check_jpg=False, check_yrd=False, check_his=False
        )

    def test_update_fails_without_modified_date(self):
        map_id = 1001

        create_map(map_id)

        url = reverse("maps:update", args=(map_id,))
        response = self.client.post(
            url,
            {},
        )

        self.assertEqual(400, response.status_code)

    def test_update_succeeds_for_malformed_date(self):
        map_id = 1001
        modified_date = "01-01-2000"

        create_map(map_id)

        url = reverse("maps:update", args=(map_id,))
        response = self.client.post(
            url,
            {
                "modified_date": modified_date,
            },
        )

        self.assertEqual(400, response.status_code)

    def test_update_fails_for_new_map_with_any_file_missing(self):
        map_id = 1001
        modified_date = "2000-01-01"
        file_combinations = (
            ("jpg_file", "yrd_file"),
            ("jpg_file", "his_file"),
            ("yrd_file", "his_file"),
        )
        url = reverse("maps:update", args=(map_id,))

        for file_combination in file_combinations:
            data = {"modified_date": modified_date}

            for filename in file_combination:
                data[filename] = BytesIO(b"file_data")

            response = self.client.post(url, data)

            self.assertEqual(400, response.status_code)
