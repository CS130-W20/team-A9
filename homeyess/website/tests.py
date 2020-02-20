from django.test import TestCase
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from models import JobPost, Ride, Profile
from views import dashboard


factory = APIRequestFactory()
dashboardview = dashboard.as_view()
dashboardviewurl = reverse('dashboard')


class VolunteerDashboardTest(TestCase):

    def setUp(self):
    	#uncofirmed rides - 2

        #confirmed rides - 2

        #finished rides - 2

        #job posts - 2
        job_1 = JobPost.objects.create(company=c_profile_1, location="loc1", wage="2$/HR", hours="9-5", job_title="testjob1", short_summary="testing1", description="test test1")
        job_2 = JobPost.objects.create(company=c_profile_2, location="loc2", wage="5$/HR", hours="10-6", job_title="testjob2", short_summary="testing2", description="test test2")

        #companies - 2
        c_user_1 = User.objects.create_user(username='testcompany1', password='12345')
        c_user_2 = User.objects.create_user(username='testcompany2', password='12345')
        c_profile_1 = Profile.objects.create(user=c_user_1, user_type=Profile.UserType.Company)
        c_profile_2 = Profile.objects.create(user=c_user_2, user_type=Profile.UserType.Company)

        #volunteers - 2
        v_user_1 = User.objects.create_user(username='testvolunteer1', password='12345')
        v_user_2 = User.objects.create_user(username='testvolunteer2', password='12345')
        v_profile_1 = Profile.objects.create(user=v_user_1, user_type=Profile.UserType.Volunteer)
        v_profile_2 = Profile.objects.create(user=v_user_2, user_type=Profile.UserType.Volunteer)

        #homeless - 2
        h_user_1 = User.objects.create_user(username='testhomeless1', password='12345')
        h_user_2 = User.objects.create_user(username='testhomeless2', password='12345')
        h_profile_1 = Profile.objects.create(user=h_user_1, user_type=Profile.UserType.Homeless)
        h_profile_2 = Profile.objects.create(user=h_user_2, user_type=Profile.UserType.Homeless)

    def test_get_unconfirmed_rides(self):
    def test_get_confirmed_rides(self):
    def test_get_finished_rides(self):
   	def test_get_job_posts(self):
   		url = reverse("dashboard", kwargs={'user_id': c_user_1})
		request = factory.get(url)   
		response = dashboard(request) 

		#expect jobs posed by company c_profle_1
		expected_response = JobPost.objects.filter(company=c_profle_1)
		self.assertEqual(response.data['job_posts'], expected_response)
		self.assertTrue(response.data['job_posts'])
		self.assertEqual(response.status_code, status.HTTP_200_OK)



from website.forms import SignUpForm
from website.models import Profile
# Create your tests here.

class SignUpFormTest(TestCase):

    data = {
        'username': 'susername',
        'first_name': 'first',
        'password1': 'hellopie',
        'password2': 'hellopie',
        'user_type': 'V',
        'car_make': 'make',
        'car_model': 'model',
        'car_plate': 'a123',
        }

    def test_volunteer_car_info_success(self):
        form = SignUpForm(self.data.copy())
        self.assertTrue(form.is_valid())

    def test_volunteer_car_info_failure(self):
        d = self.data.copy()
        d['car_make'] = ''
        form = SignUpForm(d)
        self.assertFalse(form.is_valid())
        
    def test_homeless_car_info_success(self):
        d = self.data.copy()
        d['car_model'] = ''
        d['user_type'] = 'H'
        form = SignUpForm(d)
        self.assertTrue(form.is_valid())
