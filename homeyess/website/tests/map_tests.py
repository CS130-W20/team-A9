import datetime
from datetime import timezone
from unittest import mock

from django.test import SimpleTestCase
from website.views import getDistance, getTimes, getTimeDistanceVector, filterQuerySet


class GetDistanceTest(SimpleTestCase):
    def test_distance(self):
        td_vec = [(1, 3), (27, 8), (60, 0), (4, 9), (17, 23)]
        actual_distance = getDistance(td_vec)
        expected_distance = 43
        self.assertTrue(actual_distance == expected_distance)


class GetTimesTest(SimpleTestCase):
    def test_times(self):
        interview_datetime = datetime.datetime(2020, 1, 1, 15)
        td_vec = [(1, 3), (27, 8), (60, 0), (4, 9), (17, 23)]
        expected_pickup = datetime.datetime(2020, 1, 1, 14, 33)
        expected_start = datetime.datetime(2020, 1, 1, 14, 32)
        expected_end = datetime.datetime(2020, 1, 1, 16, 21)
        expected_total = '1 hr 49 mins'
        actual_start, actual_pickup, actual_end, actual_total = getTimes(td_vec, interview_datetime)
        self.assertTrue(expected_start == actual_start)
        self.assertTrue(expected_pickup == actual_pickup)
        self.assertTrue(expected_end == actual_end)
        self.assertTrue(expected_total == actual_total)

class GetTimeDistanceVectorTest(SimpleTestCase):
    def createElement(self, status, duration, distance):
        return {
            'status': status,
            'distance': {
                'value': distance,
            },
            'duration': {
                'value': duration,
            }
        }

    def test_get_time_distance_vector(self):
        tests = [
            {
                'expected': None,
                'json': {
                    'status': 'BAD',
                },
            },
            {
                'expected': None,
                'json': {
                    'status': 'OK',
                    'rows': [
                        {
                            'elements': [
                                self.createElement('OK', 0, 0),
                                self.createElement('BAD', 0, 0),
                                self.createElement('OK', 0, 0),
                            ],
                        },
                        {
                            'elements': [
                                self.createElement('OK', 0, 0),
                                self.createElement('OK', 0, 0),
                                self.createElement('OK', 0, 0),
                            ],
                        },
                        {
                            'elements': [
                                self.createElement('OK', 0, 0),
                                self.createElement('OK', 0, 0),
                                self.createElement('OK', 0, 0),
                            ],
                        },
                    ],
                }
            },
            {
                'expected': [
                    (1, 2 * 0.000621371),
                    (100, 200 * 0.000621371),
                    (60, 0),
                    (1000, 2000 * 0.000621371),
                    (10, 20 * 0.000621371),
                ],
                'json': {
                    'status': 'OK',
                    'rows': [
                        {
                            'elements': [
                                self.createElement('BAD', 0, 0),
                                self.createElement('OK', 60, 2),
                                self.createElement('BAD', 0, 0),
                            ],
                        },
                        {
                            'elements': [
                                self.createElement('OK', 600, 20),
                                self.createElement('BAD', 0, 0),
                                self.createElement('OK', 6000, 200),
                            ],
                        },
                        {
                            'elements': [
                                self.createElement('BAD', 0, 0),
                                self.createElement('OK', 60000, 2000),
                                self.createElement('BAD', 0, 0),
                            ],
                        },
                    ],
                }
            },
        ]
        for t in tests:
            @mock.patch('website.ride_utils.getResponseJson', return_value=t['json'])
            def actual(self):
                return getTimeDistanceVector('', '', '', 60)
            self.assertTrue(t['expected'] == actual())

class FilterQuerySetTest(SimpleTestCase):
    class SimpleRide:
        class SimpleHomeless:
            def __init__(self):
                self.home_address = ''
            def __eq__(self, other):
                return self.__dict__ == other.__dict__

        def __init__(self, i_datetime, i_duration, **kwargs):
            self.interview_address = ''
            self.interview_datetime = i_datetime
            self.interview_duration = i_duration
            self.homeless = self.SimpleHomeless()
            if 'd' in kwargs:
                self.d = kwargs['d']
            if 'ed' in kwargs:
                self.ed = kwargs['ed']
            if 'sd' in kwargs:
                self.sd = kwargs['sd']
            if 'total_time' in kwargs:
                self.total_time = kwargs['total_time']
            if 'pickup_location' in kwargs:
                self.pickup_location = kwargs['pickup_location']

    def test_filter_query_set(self):
        rides = [
            self.SimpleRide(datetime.datetime(2020, 1, 1, 16, tzinfo=timezone.utc), 60), # after end time
            self.SimpleRide(datetime.datetime(2020, 1, 1, 12, tzinfo=timezone.utc), 90), # more than max_range
            self.SimpleRide(datetime.datetime(2020, 1, 1, 9, tzinfo=timezone.utc), 45), # before start time
            self.SimpleRide(datetime.datetime(2020, 1, 1, 11, tzinfo=timezone.utc), 30), # good
            self.SimpleRide(datetime.datetime(2020, 1, 1, 11, tzinfo=timezone.utc), 30), # td_vec returns None
        ]

        td_vecs = [
            [(1, 1), (1, 1), (60, 0), (1, 1), (1, 1)],
            [(1, 1), (1, 99), (90, 0), (1, 3), (1, 4)],
            [(1, 1), (1, 1), (45, 0), (1, 1), (1, 1)],
            [(1, 1), (1, 1), (30, 0), (1, 1), (1, 1)],
            None,
        ]

        pickup_infos = [
            'test_location',
            None,
            None,
            None,
            None,
        ]

        tests = [
            {
                'start': None,
                'end': None,
                'max_range': None,
                'expected': [
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 16, tzinfo=timezone.utc),
                        60,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 15, 58, tzinfo=timezone.utc),
                        ed=datetime.datetime(2020, 1, 1, 17, 2, tzinfo=timezone.utc),
                        total_time='1 hr 4 mins',
                        pickup_location='test_location'
                    ),
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 12, tzinfo=timezone.utc),
                        90,
                        d=107,
                        sd=datetime.datetime(2020, 1, 1, 11, 58, tzinfo=timezone.utc),
                        ed=datetime.datetime(2020, 1, 1, 13, 32, tzinfo=timezone.utc),
                        total_time='1 hr 34 mins',
                        pickup_location=None,
                    ),
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 9, tzinfo=timezone.utc),
                        45,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 8, 58, tzinfo=timezone.utc),
                        ed=datetime.datetime(2020, 1, 1, 9, 47, tzinfo=timezone.utc),
                        total_time='49 mins',
                        pickup_location=None,
                    ),
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 11, tzinfo=timezone.utc),
                        30,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 10, 58, tzinfo=timezone.utc),
                        ed=datetime.datetime(2020, 1, 1, 11, 32, tzinfo=timezone.utc),
                        total_time='34 mins',
                        pickup_location=None,
                    ),
                ],
            },
            {
                'start': '2020-01-01 10:00',
                'end': '2020-01-01 17:00',
                'max_range': 100,
                'expected': [
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 11, tzinfo=timezone.utc),
                        30,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 10, 58, tzinfo=timezone.utc),
                        ed=datetime.datetime(2020, 1, 1, 11, 32, tzinfo=timezone.utc),
                        total_time='34 mins',
                        pickup_location=None,
                    ),
                ]
            }
        ]
        for t in tests:
            @mock.patch('website.ride_utils.getTimeDistanceVectors', return_value=td_vecs)
            @mock.patch('website.ride_utils.getPickupLocations', return_value=pickup_infos)
            def actual(patch0, patch1):
                return filterQuerySet(rides, t['start'], t['end'], t['max_range'], '')
            actual_rides = actual()
            self.assertTrue(len(t['expected']) == len(actual_rides))
            for er, ar in zip(t['expected'], actual_rides):
                self.assertTrue(er.__dict__ == ar.__dict__)
