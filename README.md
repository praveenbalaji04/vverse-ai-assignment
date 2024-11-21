# vverse-ai-assignment

# Description
This project consists of code to read, trim and merge video files using OpenCV library.

# Preferred versions and tech-stacks
- Python : 3.12
- Django : 5.1
- OpenCV : 4.10
- Numpy : 2.1

# ENV
- NIL

# Steps to run this project:

- Clone the repo
- create a virtual env
- run `pip install -r requirements.txt` to install dependencies
- run `python manage.py migrate` to create tables with SQLite (Postgres preferred)
- run `python manage.py runserver` to run the server


# API
- Refer postman collection (Import the file using postman)


# Testcases
- Added test cases for all the API

# Coverage
- Coverage percent : 98%
- To view report: `htmlcov/index.html`

- NOTE: created config-3.py as dummy. `coverage html` command throws error without that file. You can delete if it works without it.