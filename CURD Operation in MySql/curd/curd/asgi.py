# =============================================================================
# curd/asgi.py - entry point for ASGI servers (Daphne, Uvicorn)
# =============================================================================
# Not used by "python manage.py runserver". Only needed when deploying.
# Works like wsgi.py and reads curd/settings.py.
# =============================================================================
import os

from django.core.asgi import get_asgi_application

# Use curd/settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

# The server calls this object for every request
application = get_asgi_application()
