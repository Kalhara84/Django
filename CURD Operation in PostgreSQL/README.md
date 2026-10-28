# Django + PostgreSQL User CRUD

A Django application for signing in with user records stored in PostgreSQL and managing those records through a web interface. The app maps its `Usdmast` model to the `usdmast` database table.

## Features

- Session-based login and logout using `usdmast` user records
- Dashboard with total, active, and administrator account counts
- Admin-only user listing, creation, editing, and deletion
- User form validation and creation/amendment audit fields
- Password verification for Django password hashes and legacy plaintext passwords; a legacy password is upgraded to a Django hash after a successful login
- Seed data applied by the app's initial data migration

## Requirements

- Python
- PostgreSQL
- Dependencies listed in `requirements.txt` (`Django` and `psycopg2-binary`)

## Setup

Run these commands from the repository directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a PostgreSQL database, then configure the `DATABASES["default"]` values in `curd/curd/settings.py` to match your local database name, user, password, host, and port. The checked-in settings currently use local development values; do not use them as production credentials.

Apply migrations and start the development server from the `curd` directory:

```powershell
cd curd
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. Use an account provisioned in your database to sign in. The migration seeds development accounts; their credentials are defined in the migration source and should not be used in a deployed environment. Change or remove those accounts and passwords before exposing the application.

## Routes

| Path | Purpose | Access |
| --- | --- | --- |
| `/login/` | Sign in | Public |
| `/logout/` | Sign out (POST request) | Signed in |
| `/` | Dashboard | Signed in |
| `/users/` | List user records | Administrator |
| `/users/add/` | Add a user | Administrator |
| `/users/<id>/edit/` | Edit a user | Administrator |
| `/users/<id>/delete/` | Delete a user (POST request) | Administrator |
| `/admin/` | Django admin site | Django admin authentication |

## Project layout

- `curd/curd/`: Django project configuration and root URL routes
- `curd/postgresql/`: User model, authentication, views, forms, migrations, and templates
- `curd/postgresql/static/`: Local stylesheets, Bootstrap assets, icons, and images
- `requirements.txt`: Python package dependencies

## Production note

The checked-in settings enable `DEBUG` and contain development-only secret key and database configuration. Before deployment, use private environment-specific settings for secrets and database credentials, disable debug mode, and configure allowed hosts and production static-file serving. Do not expose development seed accounts or their credentials.
