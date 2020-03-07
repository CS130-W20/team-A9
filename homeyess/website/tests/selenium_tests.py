from django.test import LiveServerTestCase
from selenium import webdriver


class SeleniumTests(LiveServerTestCase):
    def setUp(self):
        # Using Firefox because I think you need to do something extra with chrome:
        self.selenium = webdriver.Firefox()
        super(SeleniumTests, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(SeleniumTests, self).tearDown()

    def test_signup_company(self):
        # Specify the page that we wish to test:
        self.selenium.get("http://127.0.0.1:8000/accounts/signup")

        # Now we need to find the elements for the signup form:
        first_name = self.selenium.find_element_by_id("id_first_name")
        last_name = self.selenium.find_element_by_id("id_last_name")
        email = self.selenium.find_element_by_id("id_email")
        phone = self.selenium.find_element_by_id("id_phone")
        username = self.selenium.find_element_by_id("id_username")
        password1 = self.selenium.find_element_by_id("id_password1")
        password2 = self.selenium.find_element_by_id("id_password2")
        # Enumerate over options until we hit Company
        user_type = self.selenium.find_element_by_xpath("//select[@name="user_type"]/option[text()="Company"]")
        # Companies don"t need these:
        # car_plate = self.selenium.find_element_by_id("id_car_plate")
        # car_make = self.selenium.find_element_by_id("id_car_make")
        # car_model = self.selenium.find_element_by_id("id_car_model")

        submit = self.selenium.find_element_by_name("Sign up")

        # Now we interact with the page, entering all of the data:
        first_name.send_keys("John")
        last_name.send_keys("Doe")
        email.send_keys("johndoe@email.com")
        phone.send_keys("111-111-11111")
        username.send_keys("johnny420")
        password1.send_keys("ThisIsPassWord1")
        password2.send_keys("ThisIsPassWord1")
        user_type.click()
        submit.click()

        # Check that all is well:
        correct_sign_in = bool(">Post Job</a>" in self.selenium.page_source)
        if not correct_sign_in:
            self.assertTrue(False)

        # Now go ahead and try to post a job:
        self.selenium.find_element_by_xpath("//a[@label="Post Job"]").click()

        self.selenium.find_element_by_id("id_location").send_keys("123 South St.")
        self.selenium.find_element_by_id("id_wage").send_keys("12 usd/hr")
        self.selenium.find_element_by_id("id_hour").send_keys("40 hr/wk")
        self.selenium.find_element_by_id("id_job_title").send_keys("Janitor")
        self.selenium.find_element_by_id("id_short_summary").send_keys("Need someone to clean")
        self.selenium.find_element_by_id("id_description").send_keys("This is a longger description")

        self.selenium.find_element_by_xpath("//button[@label="Submit Job"]").click()

        # Check that we are in the correct dashboard:
        in_dashboard = bool("<title>Dashboard</title>" in self.selenium.page_source)
        correct_name = bool("<div>Name <div class="detail-text">John</div></div>" in self.selenium.page_source)
        correct_username = bool("<div>Username <div class="detail-text">johnny420</div></div>" in self.selenium.page_source)
        correct_email = bool("<div>E-mail <div class="detail-text">johndoe@email.com</div></div>" in self.selenium.page_source)

        if not (in_dashboard and correct_name and correct_username and correct_email):
            self.assertTrue(False)

        # Check that the job we just created exists:
        correct_job_name = bool("<td>Janitor</td>" in self.selenium.page_source)
        correct_wage = bool("<td>40 hr/wk</td>" in self.selenium.page_source)
        correct_summary = bool("<td>Need someone to clean</td>" in self.selenium.page_source)

        self.assertTrue(correct_job_name and correct_wage and correct_summary)
