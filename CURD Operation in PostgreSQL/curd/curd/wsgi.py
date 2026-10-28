# =============================================================================
# wsgi.py  -  WSGI (Web Server Gateway Interface) configuration
# =============================================================================
# WSGI is the traditional, synchronous way to serve a Django application.
# Used by servers like Gunicorn or Apache mod_wsgi in production.
#
# When you run  python manage.py runserver  Django also uses this internally.
# For async features (WebSockets, etc.) see asgi.py instead.
# =============================================================================

import os

# get_wsgi_application creates the WSGI callable that the server talks to.
from django.core.wsgi import get_wsgi_application

# Point Django to the settings file (curd/settings.py).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

# 'application' is the object the WSGI server (e.g. Gunicorn) will call for
# every incoming HTTP request.
application = get_wsgi_application()
