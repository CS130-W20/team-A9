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
website/tests/form_tests.py - test signup form validation, test post / edit jobs 

## Generating Documentation
1) cd homeyess/docs
2) make html

## Writing Documentation
1) vi homeyess/docs/source/index.rst
2) add directive
3) write doc strings in the module

## View Documentation
1) make sure the documentation is up to date by running `make html` in /homeyess/docs
2) visit https://github.com/CS130-W20/team-A9/blob/master/homeyess/docs/build/html/index.html (or /homeyess/docs/build/index.html) to see the rendered docs
