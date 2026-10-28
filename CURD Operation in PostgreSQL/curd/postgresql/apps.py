# =============================================================================
# postgresql/apps.py  -  App configuration for the "postgresql" Django app
# =============================================================================
# Every Django app has an AppConfig class that stores metadata about the app.
# Django discovers this class through the INSTALLED_APPS list in settings.py.
#
# You normally do not need to edit this file unless you want to:
#   - Change the default primary-key type
#   - Add startup code in the ready() method (e.g. connect signals)
# =============================================================================

from django.apps import AppConfig


class PostgresqlConfig(AppConfig):
    # Use BigAutoField (64-bit integer) as the default primary key for all
    # models in this app that do not explicitly define a primary key.
    # This matches the Django 3.2+ default and avoids overflow for large tables.
    default_auto_field = 'django.db.models.BigAutoField'

    # The Python package name of this app (the folder name).
    # Django uses this to find models, views, templates, etc.
    name = 'postgresql'
