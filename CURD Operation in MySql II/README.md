# curd  -  Django + MySQL (users CRUD + login + Expire module)

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your database details and secret key.
3. `python manage.py migrate`
4. `python manage.py runserver`

## On a real server (DEBUG=False)
Run `python manage.py collectstatic --noinput` after every deploy, so css/js/images load.

