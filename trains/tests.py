from datetime import datetime
from io import BytesIO
from unittest import mock

from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from override_storage import override_storage

from .models import Train, TrainState


def mock_file(filename: str) -> mock.MagicMock:
    mock_file = mock.MagicMock(spec=File, name="MockFile")
    mock_file.name = filename
    mock_file.size = 1
    return mock_file


def create_train(
    filename: str,
    from_player: str = "",
    to_player: str = "",
    upload_date: datetime = None,
    state: TrainState = TrainState.AVAILABLE,
) -> int:
    if not upload_date:
        upload_date = timezone.now()

    train = Train.objects.create(
        train_file=mock_file(filename),
        from_player=from_player,
        to_player=to_player,
        upload_date=upload_date,
        state=state,
    )
    return train.pk


@override_storage()
class TrainModelTests(TestCase):
    def test_train_file_is_stored(self):
        pk = create_train("train01.zrn")
        train = Train.objects.get(pk=pk)
        self.assertEqual("train01.zrn", train.train_file.name)


@override_storage()
class TrainIndexViewTests(TestCase):
    def test_train_index_view_is_empty_for_no_trains(self):
        url = reverse("trains:index")
        response = self.client.get(url)
        self.assertJSONEqual(response.content, [])

    def test_returns_one_train_with_one_train_in_db_and_no_filter(self):
        pk = create_train("train01.zrn")

        url = reverse("trains:index")
        response = self.client.get(url)
        self.assertJSONEqual(response.content, [{"pk": pk, "file": "train01.zrn"}])

    def test_returns_two_trains_with_two_trains_in_db_and_no_filter(self):
        pk1 = create_train("train01.zrn")
        pk2 = create_train("train02.zrn")

        url = reverse("trains:index")
        response = self.client.get(url)
        self.assertJSONEqual(
            response.content,
            [
                {"pk": pk1, "file": "train01.zrn"},
                {"pk": pk2, "file": "train02.zrn"},
            ],
        )

    def test_returns_only_trains_to_and_from_specified_player(self):
        pk1 = create_train("train01.zrn", from_player="player1", to_player="player2")
        pk2 = create_train("train02.zrn", from_player="player2", to_player="player1")
        pk3 = create_train("train03.zrn", from_player="player3", to_player="player4")

        url = reverse("trains:index")
        response = self.client.get(url, {"player": "player1"})
        self.assertJSONEqual(
            response.content,
            [
                {"pk": pk1, "file": "train01.zrn"},
                {"pk": pk2, "file": "train02.zrn"},
            ],
        )

    def test_returns_only_trains_with_names_like_request(self):
        pk1 = create_train("train01.zrn")
        pk2 = create_train("train02.zrn")

        url = reverse("trains:index")
        response = self.client.get(url, {"filename": "01"})
        self.assertJSONEqual(response.content, [{"pk": pk1, "file": "train01.zrn"}])

    def test_returns_only_trains_older_than_n_days(self):
        pk1 = create_train("train01.zrn", upload_date=datetime(2020, 1, 1))
        pk2 = create_train("train02.zrn", upload_date=datetime(2021, 1, 1))

        url = reverse("trains:index")
        response = self.client.get(url, {"upload_before": "2020-12-12"})
        self.assertJSONEqual(response.content, [{"pk": pk1, "file": "train01.zrn"}])

    def test_returns_only_undownloaded_trains(self):
        pk1 = create_train("train01.zrn", state=TrainState.AVAILABLE)
        pk2 = create_train("train02.zrn", state=TrainState.DOWNLOADED)
        url = reverse("trains:index")
        response = self.client.get(url)
        self.assertJSONEqual(response.content, [{"pk": pk1, "file": "train01.zrn"}])


@override_storage()
class TrainDownloadViewTests(TestCase):
    def test_download_fails_without_player_name(self):
        pk = create_train("train_01.zrn")
        url = reverse("trains:download", args=(pk,))
        response = self.client.post(url)
        self.assertEqual(400, response.status_code)

    def test_download_fails_with_unknown_id(self):
        url = reverse("trains:download", args=(1,))
        response = self.client.post(url, data={"player": "Player1"})
        self.assertEqual(404, response.status_code)

    def test_download_redirects_to_file_and_sets_state_and_downloader(self):
        pk = create_train("train_01.zrn")
        url = reverse("trains:download", args=(pk,))
        response = self.client.post(url, data={"player": "Player1"})

        self.assertRedirects(response, "/train_01.zrn", fetch_redirect_response=False)
        train: Train = Train.objects.get(pk=pk)

        assert TrainState.DOWNLOADED == train.state
        assert "Player1" == train.downloaded_by

    def test_download_fails_for_downloaded_file(self):
        pk = create_train("train_01.zrn", state=TrainState.DOWNLOADED)
        url = reverse("trains:download", args=(pk,))
        response = self.client.post(url, data={"player": "Player1"})

        self.assertEqual(400, response.status_code)


@override_storage()
class TrainUploadViewTests(TestCase):
    def test_upload_fails_without_file(self):
        url = reverse("trains:upload")
        response = self.client.post(url, {})
        self.assertEqual(400, response.status_code)

    def test_upload_succeeds_with_file(self):
        url = reverse("trains:upload")

        filename = "Y1234-01E02F034C0-000123-Player1-Player2.zrn"
        file_data = b"train_data"

        response = self.client.post(
            url, {"train_file": BytesIO(file_data), "filename": filename}
        )

        assert 200 == response.status_code

        trains = Train.objects.all()
        assert 1 == len(trains)

        train = trains[0]
        assert "Player1" == train.to_player
        assert "Player2" == train.from_player
        assert filename == train.train_file.name
        assert file_data == train.train_file.read()
        assert TrainState.AVAILABLE == train.state
