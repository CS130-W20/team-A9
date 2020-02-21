from django.test import TestCase, LiveServerTestCase
from website.forms import SignUpForm, PostJobForm
from website.models import Profile, JobPost

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

class PostEditJobFormTest(TestCase):

    data = {
        'location': '124 Test Dr.',
        'wage': '20 usd/hr',
        'hours': '10 hr/wk',
        'job_title': 'Janitor',
        'short_summary': 'This is a short summary',
        'description': 'This is a longer summary',
        }

    def test_post_job_success(self):
        form = PostJobForm(self.data.copy())
        self.assertTrue(form.is_valid())

    def test_post_job_failure(self):
        bad_data = self.data.copy()
        bad_data['location'] = ''
        form = PostJobForm(bad_data)
        self.assertFalse(form.is_valid())

    def test_edit_job_success(self):
        job_post = JobPost(self.data.copy())
        form = PostJobForm(instance=job_post)
        self.assertTrue(form.is_valid())
