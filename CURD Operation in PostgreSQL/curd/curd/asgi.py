# =============================================================================
# asgi.py  -  ASGI (Asynchronous Server Gateway Interface) configuration
# =============================================================================
# ASGI is a newer, async-capable way to serve Django.
# Used by servers like Daphne or Uvicorn instead of the older WSGI (wsgi.py).
#
# Django reads this file when you deploy with an ASGI server.
# For normal development (python manage.py runserver) you do not need to
# worry about this file.
# =============================================================================

import os

# get_asgi_application creates the ASGI callable that the server talks to.
from django.core.asgi import get_asgi_application

# Point Django to the settings file (curd/settings.py).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

# 'application' is the object the ASGI server (e.g. Daphne) will call for
# every incoming request.
application = get_asgi_application()
