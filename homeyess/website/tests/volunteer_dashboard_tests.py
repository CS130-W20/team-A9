import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework import status
from website.models import Ride


class VolunteerDashboardTest(TestCase):

    def setUp(self):
        self.PASSWORD = "hellopie"
        self.client = Client()
        #volunteers
        self.v1_user = User.objects.create_user(username='testvolunteer1', password=self.PASSWORD)
        self.v1_user.profile.user_type = "V"
        self.v1_user.save()

        self.v2_user = User.objects.create_user(username='testvolunteer2', password=self.PASSWORD)
        self.v2_user.profile.user_type = "V"
        self.v2_user.save()

        #homeless
        self.h1_user = User.objects.create_user(username='testhomeless1', password=self.PASSWORD)
        self.h1_user.profile.user_type = "H"
        self.h1_user.save()

        self.h2_user = User.objects.create_user(username='testhomeless2', password=self.PASSWORD)
        self.h2_user.profile.user_type = "H"
        self.h2_user.save()

        ##rides

        #unconfirmed
        start_time = timezone.now() + datetime.timedelta(days=5)
        interview_time = timezone.now() + datetime.timedelta(days=5)
        pickup_time = timezone.now() + datetime.timedelta(days=5)
        end_time = timezone.now() + datetime.timedelta(days=5)

        self.ride_1 = Ride.objects.create(homeless=self.h1_user.profile, interview_datetime=interview_time, interview_duration=30, pickup_datetime=pickup_time, interview_address='1c', interview_company="co1", end_datetime=end_time, start_datetime=start_time)

        #confirmed
        start_time = timezone.now() + datetime.timedelta(days=5)
        interview_time = timezone.now() + datetime.timedelta(days=5)
        pickup_time = timezone.now() + datetime.timedelta(days=5)
        end_time = timezone.now() + datetime.timedelta(days=5)
        self.ride_2 = Ride.objects.create(homeless=self.h2_user.profile, volunteer=self.v1_user.profile, interview_datetime=interview_time, interview_duration=30, pickup_datetime=pickup_time, interview_address='1c', interview_company="co1", end_datetime=end_time, start_datetime=start_time)


        #finished
        start_time = timezone.now() + datetime.timedelta(days=5)
        interview_time = timezone.now() - datetime.timedelta(days=5)
        pickup_time = timezone.now() - datetime.timedelta(days=5)
        end_time = timezone.now() - datetime.timedelta(days=5)
        self.ride_3 = Ride.objects.create(homeless=self.h1_user.profile, volunteer=self.v1_user.profile, interview_datetime=interview_time, interview_duration=30, pickup_datetime=pickup_time, interview_address='1c', interview_company="co1", end_datetime=end_time, start_datetime=start_time)


    def test_get_confirmed_rides(self):
        #test volunteer 1 - has confirmed ride
        self.client.login(username=self.v1_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides by volunteer v1_user
        query_expected_response = Ride.objects.filter(volunteer=self.v1_user.profile, interview_datetime__gt = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context['confirmed_rides'])
        self.assertEqual(got_response, expected_response)

        #test volunteer 2 - no confirmed ride
        self.client.login(username=self.v2_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides by volunteer v2_user
        query_expected_response = Ride.objects.filter(volunteer=self.v2_user.profile, interview_datetime__gt = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context['confirmed_rides'])
        self.assertFalse(got_response)
        self.assertEqual(got_response, expected_response)


    def test_get_finished_rides(self):
        #test volunteer 1 - has confirmed ride
        self.client.login(username=self.v1_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides by volunteer v1_user
        query_expected_response = Ride.objects.filter(volunteer=self.v1_user.profile, interview_datetime__lte = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context['finished_rides'])
        self.assertEqual(got_response, expected_response)

        #test volunteer 2 - no confirmed ride
        self.client.login(username=self.v2_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides by volunteer v2_user
        query_expected_response = Ride.objects.filter(volunteer=self.v2_user.profile, interview_datetime__lte = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context['finished_rides'])
        self.assertFalse(got_response)
        self.assertEqual(got_response, expected_response)
