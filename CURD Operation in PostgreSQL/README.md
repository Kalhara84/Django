# CURD Operation in PostgreSQL

This project is a Django web application for managing users and an Expire module using PostgreSQL as the database.

## Features

- User login and logout flow
- Admin-only user management (add, edit, delete, list)
- Dashboard with summary statistics
- Expire module with header/detail entry management
- PostgreSQL-ready schema and seeded data

## Project structure

- `curd/` - Django project root
  - `manage.py` - run Django commands
  - `curd/settings.py` - main project configuration
  - `postgresql/` - application logic, models, views, templates, forms

## Requirements

- Python 3.x
- PostgreSQL server
- Django
- psycopg2-binary

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database setup

1. Create a PostgreSQL database named `django_test`.
2. Update the database credentials in `curd/curd/settings.py` if your local PostgreSQL user/password differs.

Example configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_test',
        'USER': 'postgres',
        'PASSWORD': 'mypass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Run the project

From the project root (`CURD Operation in PostgreSQL`):

```bash
cd curd
python manage.py migrate
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Notes

- The app uses `postgresql` as the Django app name.
- Login and admin protection are handled in the app's decorators and authentication flow.
- The default login flow is based on the `Usdmast` table.

## Typical admin workflow

1. Create a user from the Users screen.
2. Log in with the user code and password.
3. Access the dashboard and Expire module.
4. Manage records through the app's forms.
