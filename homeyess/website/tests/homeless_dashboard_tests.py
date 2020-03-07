import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework import status
from website.models import Ride


class HomelessDashboardTest(TestCase):

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

        #uncofirmed
        interview_time = timezone.now() + datetime.timedelta(days=5)
        pickup_time = timezone.now() + datetime.timedelta(days=5)
        end_time = timezone.now() + datetime.timedelta(days=5)

        self.ride_1 = Ride.objects.create(homeless=self.h1_user.profile, volunteer=None, interview_datetime=interview_time, interview_duration=30, interview_address='1c', interview_company="co1")

        #confirmed
        interview_time = timezone.now() + datetime.timedelta(days=5)
        pickup_time = timezone.now() + datetime.timedelta(days=5)
        end_time = timezone.now() + datetime.timedelta(days=5)
        self.ride_2 = Ride.objects.create(homeless=self.h1_user.profile, volunteer=self.v1_user.profile, interview_datetime=interview_time, interview_duration=30, pickup_datetime=pickup_time, interview_address='1c', interview_company="co1", end_datetime=end_time)


        #finished
        interview_time = timezone.now() - datetime.timedelta(days=5)
        pickup_time = timezone.now() - datetime.timedelta(days=5)
        end_time = timezone.now() - datetime.timedelta(days=5)
        self.ride_3 = Ride.objects.create(homeless=self.h2_user.profile, volunteer=self.v1_user.profile, interview_datetime=interview_time, interview_duration=30, pickup_datetime=pickup_time, interview_address='1c', interview_company="co1", end_datetime=end_time)


    def test_get_confirmed_rides(self):
        #test homeless 1 - has confirmed upcoming ride
        self.client.login(username=self.h1_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides for homeless h1_user
        query_expected_response = Ride.objects.filter(homeless=self.h1_user.profile, interview_datetime__gt = timezone.now()).exclude(volunteer = None)
        expected_response = list(query_expected_response)
        got_response = list(response.context['confirmed_rides'])
        self.assertEqual(got_response, expected_response)

        #test homeless 2 - no confirmed upcoming ride
        self.client.login(username=self.h2_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides for homeless h2_user
        query_expected_response = Ride.objects.filter(homeless=self.h2_user.profile, interview_datetime__gt = timezone.now()).exclude(volunteer = None)
        expected_response = list(query_expected_response)
        got_response = list(response.context['confirmed_rides'])
        self.assertFalse(got_response)
        self.assertEqual(got_response, expected_response)


    def test_get_unconfirmed_rides(self):
        #test homeless 1 - has unconfirmed ride
        self.client.login(username=self.h1_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected unconfirmed upcoming rides for homeless h1_user
        query_expected_response = Ride.objects.filter(homeless=self.h1_user.profile, volunteer=None, interview_datetime__gt = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context['unconfirmed_rides'])
        self.assertEqual(got_response, expected_response)

        #test volunteer 2 - no upcoming unconfirmed ride
        self.client.login(username=self.h2_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected unconfirmed upcoming rides for homeless h2_user
        query_expected_response = Ride.objects.filter(homeless=self.h2_user.profile, volunteer=None, interview_datetime__gt = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context['unconfirmed_rides'])
        self.assertFalse(got_response)
        self.assertEqual(got_response, expected_response)
