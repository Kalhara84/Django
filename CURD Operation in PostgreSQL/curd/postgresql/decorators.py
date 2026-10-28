# =============================================================================
# postgresql/decorators.py  -  Custom view decorators for access control
# =============================================================================
# Decorators are functions that "wrap" a view to add extra behaviour before
# the real view code runs.  Apply them with @decorator_name above a view.
#
# This file provides two decorators:
#
#   @login_required   - redirect to /login/ if the user has no active session
#   @admin_required   - same as @login_required, AND reject non-admin users
#
# How the session works:
#   When a user logs in (views.py -> login_view), Django stores the user's
#   primary key in the session:  request.session["usdsno"] = user.usdsno
#   Every subsequent request carries a session cookie that lets us reload
#   the Usdmast row from the database to confirm the account is still active.
#
# Connections:
#   - models.py   defines Usdmast (the user table) and is_active_user / is_admin
#   - views.py    uses @login_required and @admin_required on view functions
#   - expire_views.py  uses @login_required on expire entry views
#   - context.py  reads request.usd (set here) to pass the user to templates
# =============================================================================

from functools import wraps  # preserves original function name/docstring when wrapping

from django.http import HttpResponseForbidden  # returns HTTP 403 Forbidden
from django.shortcuts import redirect          # send the browser to a different URL
from django.utils.http import url_has_allowed_host_and_scheme  # URL safety check
from django.urls import reverse                # turn a URL name into an actual path

# Usdmast is the user table (defined in models.py)
from .models import Usdmast


def _load_user(request):
    """
    Helper: read usdsno from the session and return the matching Usdmast row.

    Returns the Usdmast object if the session is valid and the account is active.
    Returns None if:
      - The session has no 'usdsno' key  (user never logged in)
      - The Usdmast row no longer exists (user was deleted)
      - The account is now inactive      (usdactflg = 'N')
    When None is returned, the session is flushed (cleared) so the next
    request starts clean.

    Used by both decorators below.
    """
    # Read the stored primary key from the session cookie.
    usdsno = request.session.get("usdsno")
    if not usdsno:
        # No session key -> nobody is logged in.
        return None

    # Look up the user in the database by their primary key.
    user = Usdmast.objects.filter(pk=usdsno).first()

    if user is None or not user.is_active_user:
        # User was deleted or deactivated since they logged in.
        # Destroy the session so the stale data does not linger.
        request.session.flush()
        return None

    return user


def login_required(view):
    """
    Decorator: only allow logged-in users to access the view.

    If the user is not logged in, redirect them to the login page.
    The original URL is appended as ?next=... so they are sent back
    after a successful login.

    Usage (in views.py or expire_views.py):
        @login_required
        def some_view(request):
            ...
    """
    @wraps(view)  # keep the original view's __name__ intact (important for Django internals)
    def wrapper(request, *args, **kwargs):
        user = _load_user(request)  # try to find who is logged in
        if user is None:
            # Build the login URL, e.g. "/login/"
            url = reverse("login")
            nxt = request.get_full_path()  # the URL the user was trying to visit

            # Only append ?next= if the target URL is safe (same host).
            # This prevents open-redirect attacks.
            if url_has_allowed_host_and_scheme(nxt, allowed_hosts=None):
                url += "?next=" + nxt

            return redirect(url)  # send the browser to /login/?next=...

        # Attach the Usdmast object to the request so views and templates can
        # use  request.usd  to get the current user's name, admin flag, etc.
        # context.py also reads request.usd to inject {{ usd }} into templates.
        request.usd = user
        return view(request, *args, **kwargs)  # call the real view
    return wrapper


def admin_required(view):
    """
    Decorator: only allow admin users (usdadmin = 'Y') to access the view.

    This decorator implies @login_required - if the user is not logged in
    they are redirected to /login/ first.  If they ARE logged in but not an
    admin, they receive HTTP 403 Forbidden.

    Usage (in views.py):
        @admin_required
        def user_list(request):
            ...
    """
    @wraps(view)
    @login_required  # ensure the user is logged in before checking admin flag
    def wrapper(request, *args, **kwargs):
        # is_admin is a property on Usdmast (models.py) that checks usdadmin == 'Y'
        if not request.usd.is_admin:
            return HttpResponseForbidden("Admin only")  # HTTP 403
        return view(request, *args, **kwargs)  # call the real view
    return wrapper
