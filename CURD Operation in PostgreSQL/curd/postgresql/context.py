# =============================================================================
# postgresql/context.py  -  Template context processor
# =============================================================================
# A context processor is a function that Django calls for EVERY request and
# whose return value is merged into the template context automatically.
#
# This means every template in the project can use {{ APP_NAME }} and {{ usd }}
# without the view explicitly passing them.
#
# To activate a context processor, add it to TEMPLATES -> OPTIONS -> context_processors
# in settings.py  (look for 'postgresql.context.app_context').
#
# Connections:
#   - settings.py  exports  APP_NAME  (the display name of the application)
#   - decorators.py  sets  request.usd  to the currently logged-in Usdmast object
#   - views.py / expire_views.py  rely on {{ usd }} in templates for showing
#     the logged-in user's name
# =============================================================================

from django.conf import settings  # access to settings.py variables


def app_context(request):
    """Return a dict that is added to every template's context automatically."""
    return {
        # APP_NAME comes from settings.py  (e.g. "CURD System")
        # Templates use it as {{ APP_NAME }} in the page <title> or navbar.
        "APP_NAME": settings.APP_NAME,

        # usd = the currently logged-in user (a Usdmast model instance).
        # decorators.login_required sets request.usd before calling the view.
        # If nobody is logged in (e.g. the login page itself), this is None.
        "usd": getattr(request, "usd", None),
    }
