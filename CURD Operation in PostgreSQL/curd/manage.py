#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

Role of this file:
- This is the entry point script for running Django terminal commands.
- Examples: 'python manage.py runserver', 'python manage.py migrate', 'python manage.py createsuperuser'.
- It connects your terminal commands with the project's settings and execution engine.
"""
import os
import sys


def main():
    """
    Main function to run administrative tasks.
    - Sets the default settings module so Django knows which settings to use ('curd.settings').
    - Imports and executes Django's command-line interface with the arguments passed in terminal (sys.argv).
    """
    # Point Django to the configuration settings file located in curd/settings.py
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')
    try:
        # Import Django's command line runner
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Error handling if Django is not installed or virtual environment is not activated
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Run the command supplied via sys.argv (e.g., ['manage.py', 'runserver'])
    execute_from_command_line(sys.argv)


# This standard check ensures main() is only executed if this file is run directly (not imported)
if __name__ == '__main__':
    main()

