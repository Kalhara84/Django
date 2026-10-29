# postgresql/apps.py - app registration. 'postgresql' in settings.py INSTALLED_APPS points here.
from django.apps import AppConfig


class PostgresqlConfig(AppConfig):
    # Type of the automatic id column for new models
    default_auto_field = 'django.db.models.BigAutoField'

    # Folder name of this app
    name = 'postgresql'
