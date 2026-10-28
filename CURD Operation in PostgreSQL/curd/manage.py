#!/usr/bin/env python
# =============================================================================
# manage.py  -  Django project entry point / command runner
# =============================================================================
# This is the first file Django needs.
# Run it from the command line to manage the project:
#   python manage.py runserver      -> start the web server
#   python manage.py migrate        -> apply database migrations
#   python manage.py createsuperuser -> create an admin user
#
# Django reads settings from  curd/settings.py  (see os.environ.setdefault below).
# =============================================================================

import os
import sys


def main():
    """Run administrative tasks."""
    # Tell Django which settings file to use (curd/settings.py).
    # If DJANGO_SETTINGS_MODULE is already set in the environment, this line
    # does nothing (setdefault only sets if not already present).
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

    try:
        # Import Django's command-line execution helper.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # If Django is not installed, give a helpful error message instead of
        # a confusing traceback.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # sys.argv is the list of words typed on the command line.
    # e.g.  ['manage.py', 'runserver']
    execute_from_command_line(sys.argv)


# Only run main() when this file is executed directly, not when it is imported.
if __name__ == '__main__':
    main()
