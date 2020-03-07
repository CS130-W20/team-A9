from django.test import TestCase, LiveServerTestCase
from django.test.utils import override_settings
from website.forms import SignUpForm, PostJobForm
from website.models import Profile, JobPost
from selenium import webdriver
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
        self.browser.find_element_by_id('id_phone').send_keys('202-555-0191')

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

    @override_settings(DEBUG=True)
    def test_signup_company(self):
        self.signup('C')

        while True:
            pass

    # def test_signup_volunteer(self):
    #     self.signup('V')

    # def test_signup_homeless(self):
    #     self.signup('H')
    
