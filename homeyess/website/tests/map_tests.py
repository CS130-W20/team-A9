from django.test import SimpleTestCase
from website.views import getDistance, getTimes, getTimeDistanceVector, filterQuerySet, getResponseJson
from unittest import mock
import datetime


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
        actual_start, actual_pickup, actual_end = getTimes(td_vec, interview_datetime)
        self.assertTrue(expected_start == actual_start)
        self.assertTrue(expected_pickup == actual_pickup)
        self.assertTrue(expected_end == actual_end)

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
            @mock.patch('website.views.getResponseJson', return_value=t['json'])
            def actual(self):
                return getTimeDistanceVector('', '', '', 60)
            self.assertTrue(t['expected'] == actual())

class FilterQuerySetTest(SimpleTestCase):

    class SimpleRide:
        def __init__(self, i_datetime, i_duration, **kwargs):
            self.interview_address = ''
            self.interview_datetime = i_datetime
            self.interview_duration = i_duration
            if 'd' in kwargs:
                self.d = kwargs['d']
            if 'ed' in kwargs:
                self.ed = kwargs['ed']
            if 'sd' in kwargs:
                self.sd = kwargs['sd']

    def test_filter_query_set(self):
        rides = [
            self.SimpleRide(datetime.datetime(2020, 1, 1, 16), 60), # after end time
            self.SimpleRide(datetime.datetime(2020, 1, 1, 12), 90), # more than max_range
            self.SimpleRide(datetime.datetime(2020, 1, 1, 9), 45), # before start time
            self.SimpleRide(datetime.datetime(2020, 1, 1, 11), 30), # good
            self.SimpleRide(datetime.datetime(2020, 1, 1, 11), 30), # td_vec returns None
        ]

        td_vecs = [
            [(1, 1), (1, 1), (60, 0), (1, 1), (1, 1)],
            [(1, 1), (1, 99), (90, 0), (1, 3), (1, 4)],
            [(1, 1), (1, 1), (45, 0), (1, 1), (1, 1)],
            [(1, 1), (1, 1), (30, 0), (1, 1), (1, 1)],
            None,
        ]

        tests = [
            {
                'start': None,
                'end': None,
                'max_range': None,
                'expected': [
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 16),
                        60,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 15, 58),
                        ed=datetime.datetime(2020, 1, 1, 17, 2),
                    ),
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 12),
                        90,
                        d=107,
                        sd=datetime.datetime(2020, 1, 1, 11, 58),
                        ed=datetime.datetime(2020, 1, 1, 13, 32),
                    ),
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 9),
                        45,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 8, 58),
                        ed=datetime.datetime(2020, 1, 1, 9, 47),
                    ),
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 11),
                        30,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 10, 58),
                        ed=datetime.datetime(2020, 1, 1, 11, 32),
                    ),
                ],
            },
            {
                'start': datetime.datetime(2020, 1, 1, 10),
                'end': datetime.datetime(2020, 1, 1, 17),
                'max_range': 100,
                'expected': [
                    self.SimpleRide(
                        datetime.datetime(2020, 1, 1, 11),
                        30,
                        d=4,
                        sd=datetime.datetime(2020, 1, 1, 10, 58),
                        ed=datetime.datetime(2020, 1, 1, 11, 32),
                    ),
                ]
            }
        ]
        for t in tests:
            @mock.patch('website.views.getTimeDistanceVector', side_effect=td_vecs)
            def actual(self):
                return filterQuerySet(rides, t['start'], t['end'], t['max_range'], '', '')
            actual_rides = actual()
            self.assertTrue(len(t['expected']) == len(actual_rides))
            for er, ar in zip(t['expected'], actual_rides):
                self.assertTrue(er.__dict__ == ar.__dict__)