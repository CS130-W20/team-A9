from django.test import TestCase
from website.forms import SignUpForm, PostJobForm
from website.models import Profile, JobPost

class SignUpFormTest(TestCase):

    volunteer_data = {
        'username': 'susername',
        'first_name': 'first',
        'last_name': 'last',
        'password1': 'hellopie',
        'password2': 'hellopie',
        'user_type': 'V',
        'car_make': 'make',
        'car_model': 'model',
        'car_plate': 'a123',
        'home_address': '123 main st',
    }
    homeless_data = {
        'username': 'susername',
        'first_name': 'first',
        'last_name': 'last',
        'password1': 'hellopie',
        'password2': 'hellopie',
        'user_type': 'H',
        'car_make': '',
        'car_model': '',
        'car_plate': '',
        'home_address': 'a',
    }
    company_data = {
        'username': 'susername',
        'first_name': 'first',
        'last_name': '',
        'password1': 'hellopie',
        'password2': 'hellopie',
        'user_type': 'C',
        'car_make': '',
        'car_model': '',
        'car_plate': '',
        'home_address': '',
    }

    def test_volunteer_success(self):
        form = SignUpForm(self.volunteer_data.copy())
        self.assertTrue(form.is_valid())

    def test_volunteer_failure(self):
        d = self.volunteer_data.copy()
        d['car_make'] = ''
        form = SignUpForm(d)
        self.assertFalse(form.is_valid())

    def test_homeless_success(self):
        d = self.homeless_data.copy()
        form = SignUpForm(d)
        self.assertTrue(form.is_valid())

    def test_homeless_failure(self):
        d = self.homeless_data.copy()
        d['last_name'] = ''
        form = SignUpForm(d)
        self.assertFalse(form.is_valid())

    def test_company_success(self):
        d = self.company_data.copy()
        form = SignUpForm(d)
        self.assertTrue(form.is_valid())

    def test_company_failure(self):
        d = self.company_data.copy()
        d['last_name'] = 'last'
        form = SignUpForm(d)
        self.assertFalse(form.is_valid())

class PostEditJobFormTest(TestCase):

    data = {
        'company'
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
