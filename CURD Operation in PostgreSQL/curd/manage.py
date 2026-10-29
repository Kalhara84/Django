#!/usr/bin/env python
# =============================================================================
# manage.py - starts Django commands for this project
# =============================================================================
# Examples:
#   python manage.py runserver   -> start the web server
#   python manage.py migrate     -> create/update the PostgreSQL tables
# It loads the settings from curd/settings.py.
# =============================================================================
import os
import sys


def main():
    # Tell Django which settings file to use (curd/settings.py)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Run the command typed in the terminal (runserver, migrate, ...)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
