from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse

from .models import Usdmast


def _load_user(request):
    usdsno = request.session.get("usdsno")
    if not usdsno:
        return None
    user = Usdmast.objects.filter(pk=usdsno).first()
    if user is None or not user.is_active_user:
        request.session.flush()
        return None
    return user


def login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = _load_user(request)
        if user is None:
            url = reverse("login")
            nxt = request.get_full_path()
            if url_has_allowed_host_and_scheme(nxt, allowed_hosts=None):
                url += "?next=" + nxt
            return redirect(url)
        request.usd = user          # current logged user (Usdmast row)
        return view(request, *args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.usd.is_admin:
            return HttpResponseForbidden("Admin only")
        return view(request, *args, **kwargs)
    return wrapper
