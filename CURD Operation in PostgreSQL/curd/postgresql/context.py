"""
Context Processors for 'postgresql' app.

Role of this file:
- Supplies global variables automatically to every rendered HTML template.
- Registered in settings.py under TEMPLATES -> OPTIONS -> 'context_processors'.
- Connects to:
  1. settings.py (reads settings.APP_NAME)
  2. decorators.py (reads request.usd set by @login_required)
  3. templates (base.html, dashboard.html, etc. can use {{ APP_NAME }} and {{ usd }})
"""

from django.conf import settings


def app_context(request):
    """
    Returns a dictionary of variables made available across all template renderings.
    - 'APP_NAME': Name of the application (e.g. 'JW Africa') for titles/branding.
    - 'usd': The currently logged-in Usdmast user object attached to request.
    """
    return {
        "APP_NAME": settings.APP_NAME,
        "usd": getattr(request, "usd", None),
    }

