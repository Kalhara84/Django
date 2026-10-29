# =============================================================================
# postgresql/views.py - login, logout, dashboard and the Users tab (CRUD)
# =============================================================================
# URLs are in urls.py.  Uses: auth.py (password check), decorators.py (who can open
# a page), forms.py (UserForm), models.py (Usdmast).
# Templates are in templates/postgresql/ (login.html, dashboard.html, users/...).
# =============================================================================
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .auth import authenticate_usdmast
from .decorators import admin_required, login_required
from .forms import UserForm
from .models import Usdmast


# ------------------------------------------------------------------ login
def login_view(request):
    """Show the login page and check the user code + password."""
    # Already logged in -> go to the dashboard
    if request.session.get("usdsno") and request.method == "GET":
        return redirect("dashboard")

    error = None
    usdusd = ""

    if request.method == "POST":
        # Values typed on the login form
        usdusd = request.POST.get("usdusd", "").strip()
        usdpwd = request.POST.get("usdpwd", "")

        if not usdusd or not usdpwd:
            error = "Please enter User Code and Password"
        else:
            # Check the database (auth.py)
            user, error = authenticate_usdmast(usdusd, usdpwd)

            if user:
                # Login OK: start a fresh session and remember who the user is
                request.session.flush()

                request.session["usdsno"] = user.usdsno
                request.session["usdusd"] = user.usdusd
                request.session["usdnam"] = user.usdnam or user.usdusd
                request.session["usdadmin"] = user.usdadmin

                # "Remember me" not ticked -> login ends when the browser closes
                if not request.POST.get("remember"):
                    request.session.set_expiry(0)

                # Go back to the page the user wanted, or to the dashboard
                nxt = request.GET.get("next", "")
                if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
                    return redirect(nxt)

                return redirect("dashboard")

    return render(request, "postgresql/login.html", {"error": error, "usdusd": usdusd})


@require_POST
def logout_view(request):
    """Logout button (sidebar). POST only."""
    request.session.flush()
    return redirect("login")


# -------------------------------------------------------------- dashboard
@login_required
def dashboard(request):
    """Home page after login. Counts users for the small cards."""
    stats = Usdmast.objects.aggregate(
        total=Count("usdsno"),
        # Active = not blocked, Admins = usdadmin 'Y'
        active=Count("usdsno", filter=~Q(usdactflg__iexact="N")),
        admins=Count("usdsno", filter=Q(usdadmin__iexact="Y")),
    )
    return render(request, "postgresql/dashboard.html", {"stats": stats})


# ------------------------------------------------------------- users CRUD
@admin_required
def user_list(request):
    """Users tab: table of all users."""
    users = Usdmast.objects.all().order_by("usdsno")
    return render(request, "postgresql/users/list.html", {"users": users})


@admin_required
def user_add(request):
    """Add a new user."""
    # Empty form on GET, filled form on POST
    form = UserForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        # Save to usdmast (forms.py also fills the created/updated columns)
        obj = form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' added.")
        return redirect("user_list")

    return render(request, "postgresql/users/form.html", {"form": form, "obj": None})


@admin_required
def user_edit(request, pk):
    """Edit an existing user (pk = usdsno)."""
    obj = get_object_or_404(Usdmast, pk=pk)

    # Form is filled with the saved values
    form = UserForm(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' updated.")
        return redirect("user_list")

    return render(request, "postgresql/users/form.html", {"form": form, "obj": obj})


@admin_required
@require_POST
def user_delete(request, pk):
    """Delete a user (POST only, from the delete pop-up in users/list.html)."""
    obj = get_object_or_404(Usdmast, pk=pk)

    if obj.pk == request.usd.pk:
        # Cannot delete yourself
        messages.error(request, "You cannot delete the user you are logged in as.")
    else:
        obj.delete()
        messages.success(request, f"User '{obj.usdusd}' deleted.")

    return redirect("user_list")
