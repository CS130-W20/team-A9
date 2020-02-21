# HomeYess
This webapp is a way to connect people experiencing homelessness, companies, and volunteers. Companies can post jobs for homeless people to see. Homeless people can request a ride to / from an interview. They are matched with volunteers to drive them.

## Directory Structure
/homeyess - django project  
/homeyess/homeyess - project settings (database, urls, packages)  
/homeyess/website - code for the website including views, models  
/homeyess/website/tests - unit tests, etc.
/homeyess/templates - html templates
/homeyess/docs/source - documentation (sphinx) settings
/homeyess/docs/build/html - contains docstrings rendered in html

## Installation/Run instructions
1) clone the repo
2) enter the repo
3) run $ virtualenv env
4) run $ source env/bin/activate
5) run $ pip3 install -r requirements.txt
6) set environment variables: SECRET_KEY, DB_NAME, DB_HOST, DB_PASSWORD, DB_USER, DB_PORT  
7) run the app on localhost $ python3 manage.py runserver (ctrl-c to exit)

## Testing
Tests can be run with the command `python3 manage.py test website.tests.<filename>`
The tests automatically create a test database within rds

When running Selenium tests for a certain browser, make sure that your browser's WebDriver is installed. FireFox
should have it built in, but for another browser like Chrome (found [here](https://sites.google.com/a/chromium.org/chromedriver/downloads)), make sure to install it.

website/tests/form_tests.py - test signup form validation, test post / edit jobs 
website/tests/volunteer_dashboard_tests.py - test volunteer dashboard view is returned and has correct data for upcoming and finished rides
website/tests/homeless_dashboard_tests.py - test homeless dashboard view is returned and has correct data for unconfirmed and confirmed rides
website/tests/company_dashboard_tests.py - test company dashboard view is returned and has correct data for job posts
website/tests/selenium_tests.py - test user interface for signing up (as a Company) and posting a job

## Generating Documentation
1) cd homeyess/docs
2) make html

## Writing Documentation
1) vi homeyess/docs/source/index.rst
2) add directive
3) write doc strings in the module

## View Documentation
View the docs at https://cs130-w20.github.io/team-A9/homeyess/docs/build/html/
