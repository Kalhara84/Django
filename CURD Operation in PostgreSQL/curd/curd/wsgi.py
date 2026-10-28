"""
WSGI (Web Server Gateway Interface) configuration for curd project.

Role of this file:
- WSGI is the standard specification for synchronous Python web applications to communicate with web servers.
- Used when deploying the project in production with servers such as Gunicorn, uWSGI, or Apache mod_wsgi.
"""

import os

from django.core.wsgi import get_wsgi_application

# Specify the default Django settings module to load
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

# Create the WSGI application callable that the web server uses to forward requests to Django
application = get_wsgi_application()

