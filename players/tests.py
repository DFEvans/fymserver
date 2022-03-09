from django.test import TestCase
from django.urls import reverse


# Create your tests here.
class PlayerUuidViewTests(TestCase):
    def test_players_uuid_returns_a_uuid(self):
        url = reverse("players:uuid")
        response = self.client.get(url, {"username": "Danny252"})

        self.assertEqual(200, response.status_code)
        assert "uuid" in str(response.content)
