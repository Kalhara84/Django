# =============================================================================
# postgresql/tests.py  -  Automated Unit & Integration Tests
# =============================================================================
# This file is used to write automated tests for the postgresql app using
# Django's built-in testing framework (which is built on top of Python's unittest).
#
# Running tests:
#   python manage.py test postgresql
#
# What can be tested here:
#   1. Model validations and methods:
#      - Usdmast (User model, password hashing via auth.py)
#      - Exhmast (Expire header, auto sequence numbers)
#      - Exlmast (Expire lines, foreign keys)
#   2. View responses and status codes:
#      - login_view: check redirect on correct password, failure on incorrect
#      - dashboard: check stats calculations and permission checks
#      - user_list / user_add / user_edit: check admin restriction
#      - expire_list / expire_add: check atomic save of header and lines
#   3. Access control decorators (decorators.py):
#      - Ensure unauthorized requests are redirected to /login/
# =============================================================================

from django.test import TestCase

# Create your tests here.
