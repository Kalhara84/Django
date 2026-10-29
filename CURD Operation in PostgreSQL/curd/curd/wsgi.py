# =============================================================================
# curd/wsgi.py - entry point for WSGI servers (Gunicorn, Apache, IIS)
# =============================================================================
# Not used by "python manage.py runserver". Only needed when deploying.
# Reads curd/settings.py.
# =============================================================================
import os

from django.core.wsgi import get_wsgi_application

# Use curd/settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

# The server calls this object for every request
application = get_wsgi_application()
