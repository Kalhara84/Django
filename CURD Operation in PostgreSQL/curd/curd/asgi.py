"""
ASGI (Asynchronous Server Gateway Interface) configuration for curd project.

Role of this file:
- ASGI is the modern asynchronous standard for Python web applications.
- Enables asynchronous processing such as WebSockets, HTTP/2, long-polling, and async views.
- Used when running with ASGI servers like Daphne, Uvicorn, or Hypercorn.
"""

import os

from django.core.asgi import get_asgi_application

# Specify the default Django settings module to load
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curd.settings')

# Create the ASGI application callable that async web servers interact with
application = get_asgi_application()

