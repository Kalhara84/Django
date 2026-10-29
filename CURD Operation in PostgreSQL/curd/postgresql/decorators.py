# =============================================================================
# postgresql/decorators.py - protects pages so only logged-in users can open them
# =============================================================================
# Used by: views.py and expire_views.py (@login_required, @admin_required)
# Uses:    models.py (Usdmast), the session saved by views.login_view
# =============================================================================
from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse

from .models import Usdmast


def _load_user(request):
    """Read the user id from the session and load that user from the database."""
    usdsno = request.session.get("usdsno")
    if not usdsno:
        # Nobody is logged in
        return None

    user = Usdmast.objects.filter(pk=usdsno).first()

    # User deleted or blocked after login -> clear the session
    if user is None or not user.is_active_user:
        request.session.flush()
        return None

    return user


def login_required(view):
    """Allow the page only for logged-in users."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = _load_user(request)
        if user is None:
            # Send to the login page and come back to this page after login (?next=...)
            url = reverse("login")
            nxt = request.get_full_path()
            if url_has_allowed_host_and_scheme(nxt, allowed_hosts=None):
                url += "?next=" + nxt
            return redirect(url)

        # Make the user available in views as request.usd (and {{ usd }} in templates)
        request.usd = user
        return view(request, *args, **kwargs)
    return wrapper


def admin_required(view):
    """Allow the page only for admin users (usdadmin = 'Y')."""
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.usd.is_admin:
            return HttpResponseForbidden("Admin only")
        return view(request, *args, **kwargs)
    return wrapper
