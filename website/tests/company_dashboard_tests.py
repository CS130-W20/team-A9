from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from website.models import JobPost

class CompanyDashboardTest(TestCase):

    def setUp(self):
        self.PASSWORD= "hellopie"
        self.client = Client()
        #companies

        self.c1_user = User.objects.create_user(username="testcompany1", password=self.PASSWORD)
        self.c1_user.profile.user_type = "C"
        self.c1_user.save()

        self.c2_user = User.objects.create_user(username="testcompany2", password=self.PASSWORD)
        self.c2_user.profile.user_type = "C"
        self.c2_user.save()

        #job posts
        self.job_1 = JobPost.objects.create(company=self.c1_user.profile, location="loc1", wage="2$/HR", hours="9-5", job_title="testjob1", short_summary="testing1", description="test test1")

    def test_get_job_posts(self):
        #test company 1 - has a job post

        self.client.login(username=self.c1_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected jobs posted by company c1_user
        query_expected_response = JobPost.objects.filter(company=self.c1_user.profile)
        expected_response = list(query_expected_response)
        got_response = list(response.context["job_posts"])
        self.assertEqual(got_response, expected_response)

        #test company 2 - no job posts

        self.client.login(username=self.c2_user.username, password=self.PASSWORD)
        url = "/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #expected jobs posted by company c2_user
        query_expected_response = JobPost.objects.filter(company=self.c2_user.profile)
        expected_response = list(query_expected_response)
        got_response = list(response.context["job_posts"])
        self.assertFalse(got_response)
        self.assertEqual(got_response, expected_response)
