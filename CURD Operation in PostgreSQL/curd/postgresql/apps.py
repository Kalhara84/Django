"""
Application Configuration for the 'postgresql' app.

Role of this file:
- Declares metadata and configuration settings for this specific Django app.
- Referenced in settings.py under INSTALLED_APPS as 'postgresql'.
"""
from django.apps import AppConfig


class PostgresqlConfig(AppConfig):
    # Specifies BigAutoField (64-bit integer) as default for auto-increment primary keys in this app
    default_auto_field = 'django.db.models.BigAutoField'
    
    # App name matching the directory name
    name = 'postgresql'

