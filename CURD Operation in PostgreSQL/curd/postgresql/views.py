"""
Views for 'postgresql' app.

Role of this file:
- Acts as the controller in Django's MVT (Model-View-Template) pattern.
- Receives HTTP requests, executes business logic, queries/updates database via Models/Forms,
  and returns HTTP responses or renders HTML templates.
- Connects to:
  1. models.py (queries and manipulates Usdmast records)
  2. forms.py (validates user input in UserForm)
  3. auth.py (authenticates username and password)
  4. decorators.py (@login_required, @admin_required to guard views)
  5. urls.py (functions here are mapped to specific URL paths)
  6. templates/postgresql/ (renders login.html, dashboard.html, and user list/form)
"""

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .auth import authenticate_usdmast
from .decorators import admin_required, login_required
from .forms import UserForm
from .models import Usdmast


# ------------------------------------------------------------------ Authentication Views
def login_view(request):
    """
    Handles user login:
    - If user is already logged in and visits via GET, redirects to dashboard.
    - On POST:
      1. Extracts 'usdusd' (username) and 'usdpwd' (password) from form submission.
      2. Validates credentials using authenticate_usdmast() from auth.py.
      3. On valid login:
         - Flushes previous session for security.
         - Stores user primary key (usdsno), username, full name, and admin flag into session.
         - Configures 'Remember Me' (session expiry).
         - Safely redirects to 'next' URL (if provided) or to the dashboard.
      4. On invalid login: displays error message on login.html.
    """
    # Already logged in: go straight to dashboard
    if request.session.get("usdsno") and request.method == "GET":
        return redirect("dashboard")

    error = None
    usdusd = ""
    if request.method == "POST":
        usdusd = request.POST.get("usdusd", "").strip()
        usdpwd = request.POST.get("usdpwd", "")
        
        if not usdusd or not usdpwd:
            error = "Please enter User Code and Password"
        else:
            user, error = authenticate_usdmast(usdusd, usdpwd)
            if user:
                # Login succeeded: initialize user session data
                request.session.flush()
                request.session["usdsno"] = user.usdsno
                request.session["usdusd"] = user.usdusd
                request.session["usdnam"] = user.usdnam or user.usdusd
                request.session["usdadmin"] = user.usdadmin
                
                # If 'Remember me' was NOT checked, expire session when browser closes
                if not request.POST.get("remember"):
                    request.session.set_expiry(0)
                    
                # Redirect to target page or default to dashboard
                nxt = request.GET.get("next", "")
                if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
                    return redirect(nxt)
                return redirect("dashboard")
                
    return render(request, "postgresql/login.html", {"error": error, "usdusd": usdusd})


@require_POST
def logout_view(request):
    """
    Handles user logout:
    - Restricted to POST requests to prevent malicious CSRF logout triggers.
    - Clears all session data from the server.
    - Redirects user back to the login page.
    """
    request.session.flush()
    return redirect("login")


# -------------------------------------------------------------- Dashboard View
@login_required
def dashboard(request):
    """
    Displays the main application dashboard:
    - Protected by @login_required (only logged-in users can view).
    - If user is an administrator, queries PostgreSQL database to calculate key statistics:
      * total: Total number of user accounts
      * active: Count of active accounts (usdactflg != 'N')
      * admins: Count of accounts with admin flag set (usdadmin == 'Y')
    - Renders templates/postgresql/dashboard.html.
    """
    stats = Usdmast.objects.aggregate(
        total=Count("usdsno"),
        active=Count("usdsno", filter=~Q(usdactflg__iexact="N")),
        admins=Count("usdsno", filter=Q(usdadmin__iexact="Y")),
    )
    return render(request, "postgresql/dashboard.html", {"stats": stats})


# ------------------------------------------------------------- User Master CRUD Views
@admin_required
def user_list(request):
    """
    CRUD: [READ - List]
    - Restricted to administrators via @admin_required.
    - Fetches all user master records from PostgreSQL, ordered by ID ascending.
    - Renders templates/postgresql/users/list.html.
    """
    users = Usdmast.objects.all().order_by("usdsno")
    return render(request, "postgresql/users/list.html", {"users": users})


@admin_required
def user_add(request):
    """
    CRUD: [CREATE]
    - Restricted to administrators via @admin_required.
    - On GET: Displays empty UserForm.
    - On POST: Validates input, saves new user record, automatically populates
      creation audit columns (acting_user=request.usd), displays success toast,
      and redirects back to user list.
    """
    form = UserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' added.")
        return redirect("user_list")
    return render(request, "postgresql/users/form.html", {"form": form, "obj": None})


@admin_required
def user_edit(request, pk):
    """
    CRUD: [UPDATE]
    - Restricted to administrators via @admin_required.
    - Retrieves existing user by primary key (pk) or raises 404 Not Found.
    - On GET: Displays UserForm pre-filled with the user's current data.
    - On POST: Validates and updates user, updates amendment audit columns
      (acting_user=request.usd), displays success message, and redirects to user list.
    """
    obj = get_object_or_404(Usdmast, pk=pk)
    form = UserForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' updated.")
        return redirect("user_list")
    return render(request, "postgresql/users/form.html", {"form": form, "obj": obj})


@admin_required
@require_POST
def user_delete(request, pk):
    """
    CRUD: [DELETE]
    - Restricted to administrators and requires POST request.
    - Safety check: Prevents an admin from deleting their own currently logged-in account.
    - Permanently removes user record from PostgreSQL table 'usdmast'.
    - Displays flash message and redirects to user list.
    """
    obj = get_object_or_404(Usdmast, pk=pk)
    if obj.pk == request.usd.pk:
        messages.error(request, "You cannot delete the user you are logged in as.")
    else:
        obj.delete()
        messages.success(request, f"User '{obj.usdusd}' deleted.")
    return redirect("user_list")

