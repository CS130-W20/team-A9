from django.test import TestCase, LiveServerTestCase
from django.test.utils import override_settings
from website.forms import SignUpForm, PostJobForm
from website.models import Profile, JobPost
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys

class SeleniumTests(LiveServerTestCase):
    def setUp(self):
        # Using ChromeDriver here:
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
        self.browser.maximize_window()
        super(SeleniumTests, self).setUp()

    def tearDown(self):
        self.browser.quit()
        super(SeleniumTests, self).tearDown()

    #
    # Tests if we can signup correctly:
    #

    def signup(self, profile_type):
        self.browser.get(self.live_server_url)

        # First we go ahead and signup:
        self.browser.find_element_by_xpath('//*[@id="navbarNav"]/ul/li[1]/a').click()

        if profile_type == 'V':
            self.browser.find_element_by_id('id_user_type_0').click()
        elif profile_type == 'H':
            self.browser.find_element_by_id('id_user_type_1').click()
        elif profile_type == 'C':
            self.browser.find_element_by_id('id_user_type_2').click()

        # Click on the signup button:
        self.browser.find_element_by_xpath('/html/body/div[1]/div/form/button').click()

        # Shared by all profile types:
        self.browser.find_element_by_id('id_username').send_keys('usr_johndoe')
        self.browser.find_element_by_id('id_password1').send_keys('iNdJDopX2Q')
        self.browser.find_element_by_id('id_password2').send_keys('iNdJDopX2Q')
        self.browser.find_element_by_id('id_email').send_keys('john@doe.com')
        self.browser.find_element_by_id('id_phone').send_keys('2025550191')

        if profile_type == 'C':
            self.browser.find_element_by_id('id_first_name').send_keys('Doe Inc.')

        # Signup sheet things that are shared:
        if profile_type == 'V' or profile_type == 'H':
            self.browser.find_element_by_id('id_first_name').send_keys('John')
            self.browser.find_element_by_id('id_last_name').send_keys('Doe')
            # Pickup address for homeless people:
            self.browser.find_element_by_id('id_home_address').send_keys('123 Fake Dr.')

        if profile_type == 'V':
            self.browser.find_element_by_id('id_car_plate').send_keys('6XLR581')
            self.browser.find_element_by_id('id_car_make').send_keys('Corolla')
            self.browser.find_element_by_id('id_car_model').send_keys('Toyota')

        # Now we go ahead and click it:
        self.browser.find_element_by_xpath('/html/body/div[1]/div/form/button').click()

    def test_signup_company(self):
        self.signup('C')
        time.sleep(3)
        self.assertTrue('Post Job' in self.browser.page_source)

    def test_signup_volunteer(self):
        self.signup('V')
        time.sleep(3)
        self.assertTrue('Volunteer to drive' in self.browser.page_source)

    def test_signup_homeless(self):
        self.signup('H')
        time.sleep(3)
        self.assertTrue('Request Ride' in self.browser.page_source)

    #
    # Tests if we can login correctly:
    #

    def login(self):
        # Click the login button:
        self.browser.find_element_by_xpath('//*[@id="navbarNav"]/ul/li[2]/a').click()
        self.browser.find_element_by_id('id_username').send_keys('usr_johndoe')
        self.browser.find_element_by_id('id_password').send_keys('iNdJDopX2Q')
        # Click login
        self.browser.find_element_by_xpath('/html/body/div[1]/div/form/button').click()

    def test_logout_login_company(self):
        self.signup('C')
        self.browser.find_element_by_xpath('//*[@id="navbarNav"]/ul/li[3]/a').click()
        self.login()
        time.sleep(3)
        self.assertTrue('Post Job' in self.browser.page_source)

    def test_logout_login_volunteer(self):
        self.signup('V')
        self.browser.find_element_by_xpath('//*[@id="navbarNav"]/ul/li[3]/a').click()
        self.login()
        time.sleep(3)
        self.assertTrue('Volunteer to drive' in self.browser.page_source)

    def test_logout_login_homeless(self):
        self.signup('H')
        self.browser.find_element_by_xpath('//*[@id="navbarNav"]/ul/li[4]/a').click()
        self.login()
        time.sleep(3)
        self.assertTrue('Request Ride' in self.browser.page_source)

    #
    # Test specific use cases for each of the profiles:
    #

    def post_job(self):
        self.browser.find_element_by_xpath('//*[@id="navbarNav"]/ul/li[2]/a').click()
        self.browser.find_element_by_id('id_location').send_keys('1 Job Dr.')
        self.browser.find_element_by_id('id_wage').send_keys('30 USD/hr')
        self.browser.find_element_by_id('id_hours').send_keys('40 hr/wk')
        self.browser.find_element_by_id('id_job_title').send_keys('Janitor')
        self.browser.find_element_by_id('id_short_summary').send_keys('This is a short summary for the job provided.')
        self.browser.find_element_by_id('id_description').send_keys('This is a longer description of the job provided.')
        self.browser.find_element_by_xpath('/html/body/div[1]/div/form/button').click()

    def test_post_job_and_delete(self):
        self.signup('C')
        time.sleep(3)
        self.post_job()
        time.sleep(3)
        # Check that the job was posted correctly:
        self.assertTrue('Janitor' in self.browser.page_source)
        self.assertTrue('30 USD/hr' in self.browser.page_source)
        self.assertTrue('This is a short summary for the job provided.' in self.browser.page_source)
        # Now click on details (there should only be one job currently):
        self.browser.find_element_by_link_text('Details').click()
        # Now attempt to delete the job:
        self.browser.find_element_by_xpath('/html/body/div[1]/div/form/button[2]').click()
        self.assertTrue('No jobs posts yet. Post a job now!' in self.browser.page_source)
