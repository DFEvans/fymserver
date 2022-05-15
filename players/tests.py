from typing import Any, Dict

from django.core import mail
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from players.decorators import valid_player_required
from players.views import generate_otp

from .models import Player


def create_player(username: str, token: str, email: str = "test@localhost") -> Player:
    player_obj: Player = Player.objects.create(
        username=username,
        token=token,
        email=email,
    )
    player_obj.save()
    return player_obj


OK_USERNAME = "Player1"
BAD_USERNAME = "qwerty"
OK_TOKEN = "abc123"
BAD_TOKEN = "def456"


def create_default_player() -> Player:
    return create_player(OK_USERNAME, OK_TOKEN)


@valid_player_required
def wrapped_func(request: HttpRequest, message: str = "ok"):
    return message


class FakeRequest:
    def __init__(self, post_params: Dict[str, Any]) -> None:
        self.POST = post_params


class TestValidPlayerRequired(TestCase):
    def test_should_return_called_func_if_valid(self):
        create_default_player()

        expected = "ok"
        actual = wrapped_func(
            FakeRequest(
                {
                    "player": OK_USERNAME,
                    "token": OK_TOKEN,
                }
            )
        )

        assert expected == actual

    def test_should_raise_if_invalid_token(self):
        create_default_player()

        with self.assertRaises(PermissionDenied):
            wrapped_func(
                FakeRequest(
                    {
                        "player": OK_USERNAME,
                        "token": BAD_TOKEN,
                    }
                )
            )

    def test_should_raise_if_unknown_user(self):
        create_default_player()

        with self.assertRaises(PermissionDenied):
            wrapped_func(
                FakeRequest(
                    {
                        "player": BAD_USERNAME,
                        "token": OK_TOKEN,
                    }
                )
            )

    def test_should_raise_if_missing_user(self):
        create_default_player()

        with self.assertRaises(BadRequest):
            wrapped_func(
                FakeRequest(
                    {
                        "token": OK_TOKEN,
                    }
                )
            )

    def test_should_raise_if_missing_token(self):
        create_default_player()

        with self.assertRaises(BadRequest):
            wrapped_func(
                FakeRequest(
                    {
                        "player": OK_USERNAME,
                    }
                )
            )

    def test_should_pass_args(self):
        create_default_player()

        expected = "test_message"
        actual = wrapped_func(
            FakeRequest(
                {
                    "player": OK_USERNAME,
                    "token": OK_TOKEN,
                }
            ),
            message="test_message",
        )

        assert expected == actual


class TestPlayerSendAuthCode(TestCase):
    def setUp(self):
        create_default_player()

    def test_fails_for_no_player_name(self):
        url = reverse("players:send_auth_code")
        response = self.client.post(url)
        self.assertEqual(400, response.status_code)

    def test_sends_email_for_known_player_name(self):
        url = reverse("players:send_auth_code")
        response = self.client.post(url, data={"player": OK_USERNAME})

        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(
            "[Freight Yard Manager] Authentication Code", mail.outbox[0].subject
        )

    def test_does_not_send_email_for_unknown_player_name(self):
        url = reverse("players:send_auth_code")
        response = self.client.post(url, data={"player": BAD_USERNAME})

        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(mail.outbox))

    def test_does_not_send_email_for_blank_email(self):
        create_player(
            "Player2",
            OK_TOKEN,
            "",
        )

        url = reverse("players:send_auth_code")
        response = self.client.post(url, data={"player": "Player2"})

        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(mail.outbox))


class TestGenerateOTP(TestCase):
    def test_generates_expected_value(self):
        key = "secretkey"
        step = 1000000000000000
        timestamp = 0
        drift = 0

        expected = 49381
        actual = generate_otp(key, step, timestamp, drift=drift)

        assert expected == actual
