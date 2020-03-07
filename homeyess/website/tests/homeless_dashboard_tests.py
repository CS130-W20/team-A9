import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from website.models import Ride

client = Client()

class VolunteerDashboardTest(TestCase):

    def setUp(self):
        #volunteers
        self.v1_user = User.objects.create_user(username="testvolunteer1", password="hellopie")
        self.v1_user.profile.user_type = "V"
        self.v1_user.save()

        self.v2_user = User.objects.create_user(username="testvolunteer2", password="hellopie")
        self.v2_user.profile.user_type = "V"
        self.v2_user.save()

        #homeless
        self.h1_user = User.objects.create_user(username="testhomeless1", password="hellopie")
        self.h1_user.profile.user_type = "H"
        self.h1_user.save()

        self.h2_user = User.objects.create_user(username="testhomeless2", password="hellopie")
        self.h2_user.profile.user_type = "H"
        self.h2_user.save()

        ##rides

        #uncofirmed
        interview_time = timezone.now() + datetime.timedelta(days=5)
        pickup_time = timezone.now() + datetime.timedelta(days=5)
        end_time = timezone.now() + datetime.timedelta(days=5)

        self.ride_1 = Ride.objects.create(homeless=self.h1_user.profile, volunteer=None, interview_datetime=interview_time, interview_duration=30, volunteer_address="1a", pickup_address="1b", pickup_datetime=pickup_time, interview_address="1c", interview_company="co1", end_datetime=end_time, ride_status="U")
        
        #confirmed
        interview_time = timezone.now() + datetime.timedelta(days=5)
        pickup_time = timezone.now() + datetime.timedelta(days=5)
        end_time = timezone.now() + datetime.timedelta(days=5)
        self.ride_2 = Ride.objects.create(homeless=self.h1_user.profile, volunteer=self.v1_user.profile, interview_datetime=interview_time, interview_duration=30, volunteer_address="1a", pickup_address="1b", pickup_datetime=pickup_time, interview_address="1c", interview_company="co1", end_datetime=end_time, ride_status="U")
        

        #finished
        interview_time = timezone.now() - datetime.timedelta(days=5)
        pickup_time = timezone.now() - datetime.timedelta(days=5)
        end_time = timezone.now() - datetime.timedelta(days=5)
        self.ride_3 = Ride.objects.create(homeless=self.h2_user.profile, volunteer=self.v1_user.profile, interview_datetime=interview_time, interview_duration=30, volunteer_address="1a", pickup_address="1b", pickup_datetime=pickup_time, interview_address="1c", interview_company="co1", end_datetime=end_time, ride_status="U")
        

    def test_get_confirmed_rides(self):
        #test homeless 1 - has confirmed upcoming ride
        url = reverse("dashboard", kwargs={"user_id": self.h1_user.pk})
        url = "/dashboard/" + str(self.h1_user.pk) + "/"
        response = client.get(url)   

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides for homeless h1_user
        query_expected_response = Ride.objects.filter(homeless=self.h1_user.profile, interview_datetime__gt = timezone.now()).exclude(volunteer = None)
        expected_response = list(query_expected_response)
        got_response = list(response.context["confirmed_rides"])
        self.assertEqual(got_response, expected_response)

        #test homeless 2 - no confirmed upcoming ride
        url = reverse("dashboard", kwargs={"user_id": self.h2_user.pk})
        url = "/dashboard/" + str(self.h2_user.pk) + "/"
        response = client.get(url)   

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected confirmed upcoming rides for homeless h2_user
        query_expected_response = Ride.objects.filter(homeless=self.h2_user.profile, interview_datetime__gt = timezone.now()).exclude(volunteer = None)
        expected_response = list(query_expected_response)
        got_response = list(response.context["confirmed_rides"])
        self.assertFalse(got_response)
        self.assertEqual(got_response, expected_response)
        

    def test_get_unconfirmed_rides(self):
        #test homeless 1 - has unconfirmed ride
        url = reverse("dashboard", kwargs={"user_id": self.h1_user.pk})
        url = "/dashboard/" + str(self.h1_user.pk) + "/"
        response = client.get(url)   

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected unconfirmed upcoming rides for homeless h1_user
        query_expected_response = Ride.objects.filter(homeless=self.h1_user.profile, volunteer=None, interview_datetime__gt = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context["unconfirmed_rides"])
        self.assertEqual(got_response, expected_response)

        #test volunteer 2 - no upcoming unconfirmed ride
        url = reverse("dashboard", kwargs={"user_id": self.h2_user.pk})
        url = "/dashboard/" + str(self.h2_user.pk) + "/"
        response = client.get(url)   

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected unconfirmed upcoming rides for homeless h2_user
        query_expected_response = Ride.objects.filter(homeless=self.h2_user.profile, volunteer=None, interview_datetime__gt = timezone.now())
        expected_response = list(query_expected_response)
        got_response = list(response.context["unconfirmed_rides"])
        self.assertFalse(got_response)
        self.assertEqual(got_response, expected_response)

