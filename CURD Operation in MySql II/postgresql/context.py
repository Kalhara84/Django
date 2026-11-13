# =============================================================================
# postgresql/context.py - values available in every HTML template
# =============================================================================
# Registered in curd/settings.py (TEMPLATES -> context_processors).
#   {{ APP_NAME }} -> used in base.html and login.html
#   {{ usd }}      -> logged-in user, set by postgresql/decorators.py (login_required)
# =============================================================================
from django.conf import settings


def app_context(request):
    return {
        # App name from settings.py
        "APP_NAME": settings.APP_NAME,

        # Logged-in Usdmast row (None on the login page)
        "usd": getattr(request, "usd", None),
    }
