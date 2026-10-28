"""
URL configuration for curd project.

Role of this file:
- This is the main URL router (project-level URLconf) for the entire Django application.
- When an incoming HTTP request arrives, Django checks these patterns from top to bottom.
- It routes traffic to the Django admin panel or forwards requests to the 'postgresql' app's URLs.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Built-in Django administrative portal (accessible at /admin/)
    path('admin/', admin.site.urls),
    
    # Routes all other requests (starting at root "") to the postgresql app's URL configuration
    # Connects to: curd/postgresql/urls.py
    path('', include('postgresql.urls')),
]

