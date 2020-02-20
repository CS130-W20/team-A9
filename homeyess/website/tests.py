from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from website.models import JobPost, Ride, Profile
from website.views import dashboard
from website.forms import SignUpForm

client = Client()
factory = RequestFactory()

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
