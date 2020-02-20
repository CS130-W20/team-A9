from django.test import TestCase
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
