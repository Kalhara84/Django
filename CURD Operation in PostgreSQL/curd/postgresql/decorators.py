"""
Custom View Decorators for 'postgresql' app.

Role of this file:
- Provides security checks before executing views.
- Restricts view access based on user session status and role permissions.
- Connects to:
  1. models.py (queries Usdmast by primary key stored in session)
  2. views.py (decorated with @login_required and @admin_required)
"""

from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse

from .models import Usdmast


def _load_user(request):
    """
    Helper function to load the logged-in user from the active session.
    - Reads 'usdsno' (primary key) from request.session.
    - Checks if the user still exists in PostgreSQL and is active (not blocked).
    - If user doesn't exist or was blocked, flushes/clears the session.
    - Returns the Usdmast model instance, or None.
    """
    usdsno = request.session.get("usdsno")
    if not usdsno:
        return None
    user = Usdmast.objects.filter(pk=usdsno).first()
    if user is None or not user.is_active_user:
        request.session.flush()
        return None
    return user


def login_required(view):
    """
    Decorator for views that require user authentication.
    - Checks if user is logged in via session.
    - If NOT logged in: redirects to login page with '?next=<current_url>' so user returns after login.
    - If logged in: attaches the loaded user object to 'request.usd' and proceeds to the view.
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = _load_user(request)
        if user is None:
            # Build redirect URL to login with safe 'next' query param
            url = reverse("login")
            nxt = request.get_full_path()
            if url_has_allowed_host_and_scheme(nxt, allowed_hosts=None):
                url += "?next=" + nxt
            return redirect(url)
        # Attach user to request object so views and templates can access it as request.usd
        request.usd = user
        return view(request, *args, **kwargs)
    return wrapper


def admin_required(view):
    """
    Decorator for views that require administrator privileges (usdadmin == 'Y').
    - Inherits @login_required to ensure user is logged in first.
    - Checks if user.is_admin property returns True.
    - If user is NOT an admin: returns HTTP 403 Forbidden response.
    - If user IS an admin: proceeds to the view.
    """
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.usd.is_admin:
            return HttpResponseForbidden("Admin only")
        return view(request, *args, **kwargs)
    return wrapper

