from django.test import TestCase
from datetime import datetime

from hf_alerts.utils import get_availabilities, Availability

class TestAvailabilities(TestCase):

    def test_availabilities(self):
        availabilities = get_availabilities(
            bookings=[
                {'type': 4, 'start': '2021-12-15T00:00:00+01:00', 'end': '2021-12-15T10:00:00+01:00', 'band': None},
                {'type': 1, 'start': '2021-12-15T11:00:00+01:00', 'end': '2021-12-15T13:00:00+01:00',
                  'band': {'id': 1885333, 'name': 'Alain Damien - Elite Music', 'short_name': 'Alain Dami'}},
                {'type': 1, 'start': '2021-12-15T15:00:00+01:00', 'end': '2021-12-15T19:30:00+01:00',
                  'band': {'id': 1885333, 'name': 'Alain Damien - Elite Music', 'short_name': 'Alain Dami'}},
                {'type': 1, 'start': '2021-12-15T20:00:00+01:00', 'end': '2021-12-15T22:00:00+01:00',
                  'band': {'id': 2300383, 'name': 'Vincent Cohas', 'short_name': 'Vincent Co'}}],
            open='2021-12-15T10:00:00+01:00',
            close='2021-12-16T00:00:00+01:00'
        )
        test_availabilities = [
            Availability(datetime.fromisoformat('2021-12-15T10:00:00+01:00'), datetime.fromisoformat('2021-12-15T11:00:00+01:00')),
            Availability(datetime.fromisoformat('2021-12-15T13:00:00+01:00'), datetime.fromisoformat('2021-12-15T15:00:00+01:00')),
            Availability(datetime.fromisoformat('2021-12-15T19:30:00+01:00'), datetime.fromisoformat('2021-12-15T20:00:00+01:00')),
            Availability(datetime.fromisoformat('2021-12-15T22:00:00+01:00'), datetime.fromisoformat('2021-12-16T00:00:00+01:00'))
        ]
        self.assertListEqual(availabilities, test_availabilities)