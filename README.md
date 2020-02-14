# HomeYess
This webapp is a way to connect people experiencing homelessness, companies, and volunteers. Companies can post jobs for homeless people to see. Homeless people can request a ride to / from an interview. They are matched with volunteers to drive them.

## Directory Structure
/homeyess - django project  
/homeyess/homeyess - project settings (database, urls, packages)  
/homeyess/website - code for the website including views, models  

## Installation/Run instructions
1) clone the repo
2) enter the repo
3) run $ virtualenv env
4) run $ pip3 install -r requirements.txt
5) set environment variable SECRET_KEY  
6) run the app on localhost $ python3 manage.py runserver (ctrl-c to exit)

## Relevant Links 

## Generating documentation instructions
1) cd docs
2) make html

## Writing documentation instructions
1) vi docs/source/index.rst
2) add directive
3) write doc strings in the module
