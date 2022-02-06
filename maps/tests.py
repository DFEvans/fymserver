from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Map


# Create your tests here.
class MapsIndexViewTests(TestCase):
    def test_works(self):
        response = self.client.get(reverse("maps:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world!")


class MapModelTests(TestCase):
    def test_map_id_1001_should_be_valid(self):
        map = Map(map_id=1001, modified_date=timezone.now())
        self.assertEqual(1001, map.map_id)

    def test_modified_date_is_stored(self):
        mod_date = timezone.datetime(2020, 1, 1, 0, 0, 0)
        map = Map(map_id=1001, modified_date=mod_date)
        self.assertEqual(mod_date, map.modified_date)
