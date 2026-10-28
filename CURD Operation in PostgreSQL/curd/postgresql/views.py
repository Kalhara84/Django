# =============================================================================
# postgresql/views.py  -  View functions for login, dashboard, and user CRUD
# =============================================================================
# Views are Python functions that receive an HTTP request and return an HTTP
# response (usually a rendered HTML page or a redirect).
#
# This file handles:
#   /login/            -> login_view()   show login form; authenticate on POST
#   /logout/           -> logout_view()  clear session; redirect to /login/
#   /                  -> dashboard()    home page with summary stats
#   /users/            -> user_list()    list all users (admin only)
#   /users/add/        -> user_add()     add a new user (admin only)
#   /users/<pk>/edit/  -> user_edit()    edit an existing user (admin only)
#   /users/<pk>/delete/-> user_delete()  delete a user (admin only, POST only)
#
# URL routing is defined in postgresql/urls.py.
# Authentication logic lives in auth.py.
# Access control decorators are in decorators.py.
# The UserForm form class is in forms.py.
#
# Connections:
#   - auth.py        -> authenticate_usdmast() called from login_view()
#   - decorators.py  -> @login_required, @admin_required applied to views
#   - forms.py       -> UserForm used in user_add() and user_edit()
#   - models.py      -> Usdmast queried for dashboard stats and user CRUD
#   - templates      -> postgresql/login.html, dashboard.html, users/*.html
# =============================================================================

from django.contrib import messages                        # flash messages shown in templates
from django.db.models import Count, Q                     # database aggregation helpers
from django.shortcuts import get_object_or_404, redirect, render  # common view shortcuts
from django.utils.http import url_has_allowed_host_and_scheme     # URL safety validation
from django.views.decorators.http import require_POST             # restrict view to POST only

# Internal imports from this app.
from .auth import authenticate_usdmast          # login logic (auth.py)
from .decorators import admin_required, login_required  # access control (decorators.py)
from .forms import UserForm                     # user create/edit form (forms.py)
from .models import Usdmast                    # user table (models.py)


# =============================================================================
# LOGIN
# =============================================================================
def login_view(request):
    """
    Show the login page (GET) and process login credentials (POST).

    GET:   Render the login form (postgresql/login.html).
    POST:  Read usdusd and usdpwd from the form, call authenticate_usdmast(),
           store user info in the session, then redirect to dashboard (or ?next=).

    If "Remember me" checkbox is NOT ticked, the session expires when the
    browser is closed (set_expiry(0)).

    Template: postgresql/templates/postgresql/login.html
    """
    # If the user already has an active session and hits the login page via GET,
    # send them straight to the dashboard (no need to log in again).
    if request.session.get("usdsno") and request.method == "GET":
        return redirect("dashboard")

    error = None    # error message to show on the form if login fails
    usdusd = ""     # preserve the typed user code so the user does not have to retype it

    if request.method == "POST":
        # Read the values the user typed into the form.
        usdusd = request.POST.get("usdusd", "").strip()
        usdpwd = request.POST.get("usdpwd", "")

        # Basic check: both fields must be filled in.
        if not usdusd or not usdpwd:
            error = "Please enter User Code and Password"
        else:
            # Delegate authentication to auth.py -> authenticate_usdmast().
            # Returns (user_object, None) on success or (None, "error text") on failure.
            user, error = authenticate_usdmast(usdusd, usdpwd)

            if user:
                # Login succeeded.
                # Flush any old session data first (security: prevents session fixation).
                request.session.flush()

                # Store minimal user info in the session cookie.
                # decorators.py -> _load_user() reads usdsno to reload the full object
                # on subsequent requests.
                request.session["usdsno"] = user.usdsno    # primary key
                request.session["usdusd"] = user.usdusd    # user code (login name)
                request.session["usdnam"] = user.usdnam or user.usdusd  # display name
                request.session["usdadmin"] = user.usdadmin             # 'Y' or ''

                # If "Remember me" was NOT checked, expire the session when the
                # browser closes (set_expiry(0) = session cookie, not persistent).
                if not request.POST.get("remember"):
                    request.session.set_expiry(0)

                # Redirect to the originally requested page if ?next= was in the URL,
                # but only if the URL is safe (same host) to prevent open redirects.
                nxt = request.GET.get("next", "")
                if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
                    return redirect(nxt)

                # Default: go to the dashboard.
                return redirect("dashboard")

    # Render the login form, passing any error message and the typed user code.
    return render(request, "postgresql/login.html", {"error": error, "usdusd": usdusd})


# =============================================================================
# LOGOUT
# =============================================================================
@require_POST   # Only accept POST requests (protects against CSRF / link-based logout)
def logout_view(request):
    """
    Clear the user's session and redirect to the login page.

    @require_POST ensures this can only be triggered by a form submission
    (e.g. a logout button), not by someone clicking a link.
    """
    request.session.flush()     # destroy all session data (logs the user out)
    return redirect("login")    # send the browser to /login/


# =============================================================================
# DASHBOARD
# =============================================================================
@login_required  # User must be logged in; otherwise redirected to /login/
def dashboard(request):
    """
    Home page shown after login.  Displays a summary of user statistics.

    Queries:
      total  - total number of user accounts
      active - accounts that are NOT disabled (usdactflg != 'N')
      admins - accounts where usdadmin = 'Y'

    Template: postgresql/templates/postgresql/dashboard.html
    Context:  {"stats": {"total": N, "active": N, "admins": N}}
    """
    # Run a single SQL query that counts all three values at once using
    # Django's aggregate() with conditional Count(filter=...).
    stats = Usdmast.objects.aggregate(
        total=Count("usdsno"),
        # ~Q(usdactflg__iexact="N") means "NOT (usdactflg = 'N' case-insensitive)"
        active=Count("usdsno", filter=~Q(usdactflg__iexact="N")),
        admins=Count("usdsno", filter=Q(usdadmin__iexact="Y")),
    )
    return render(request, "postgresql/dashboard.html", {"stats": stats})


# =============================================================================
# USER CRUD  (Create, Read, Update, Delete)
# =============================================================================

@admin_required  # Must be logged in AND be an admin (usdadmin = 'Y')
def user_list(request):
    """
    Show a table of all users ordered by primary key.

    Template: postgresql/templates/postgresql/users/list.html
    Context:  {"users": QuerySet of all Usdmast rows}
    """
    users = Usdmast.objects.all().order_by("usdsno")
    return render(request, "postgresql/users/list.html", {"users": users})


@admin_required
def user_add(request):
    """
    Show a blank user form (GET) and create a new user (POST).

    GET:   Render an empty UserForm.
    POST:  Validate the form; if valid, save the new user and redirect to
           the user list with a success flash message.

    Template: postgresql/templates/postgresql/users/form.html
    Context:  {"form": UserForm, "obj": None}  (obj=None signals "add" mode to template)
    """
    # request.POST or None:
    #   - On GET, request.POST is empty so None is passed -> unbound form (blank).
    #   - On POST, the submitted data is bound to the form for validation.
    form = UserForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        # form.save() fills in audit columns and hashes the password (see forms.py).
        # request.usd is the logged-in admin user (set by @admin_required / decorators.py).
        obj = form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' added.")
        return redirect("user_list")  # go back to the list after saving

    return render(request, "postgresql/users/form.html", {"form": form, "obj": None})


@admin_required
def user_edit(request, pk):
    """
    Show a pre-filled user form (GET) and update an existing user (POST).

    pk    - the primary key from the URL, e.g. /users/5/edit/ gives pk=5.

    GET:   Load the Usdmast row with that pk and pre-fill the form.
    POST:  Validate and save changes, then redirect to the user list.

    get_object_or_404() automatically returns HTTP 404 if no row with that pk
    exists, which is cleaner than letting an exception bubble up.

    Template: postgresql/templates/postgresql/users/form.html
    Context:  {"form": UserForm, "obj": Usdmast instance}
    """
    # Load the user to edit, or show 404 if not found.
    obj = get_object_or_404(Usdmast, pk=pk)

    # Bind the form to the existing instance so existing values appear in fields.
    form = UserForm(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' updated.")
        return redirect("user_list")

    return render(request, "postgresql/users/form.html", {"form": form, "obj": obj})


@admin_required
@require_POST   # Deletion must be triggered by a form POST, not a browser link
def user_delete(request, pk):
    """
    Delete a user account.

    pk    - primary key of the user to delete.

    Safety check: an admin cannot delete the account they are currently
    logged in as (prevents accidental self-lockout).

    After deleting (or showing an error), redirects back to the user list.
    messages.success / messages.error show flash banners in the template.
    """
    # Load the user to delete, or show 404 if not found.
    obj = get_object_or_404(Usdmast, pk=pk)

    if obj.pk == request.usd.pk:
        # The admin is trying to delete their own account - block it.
        messages.error(request, "You cannot delete the user you are logged in as.")
    else:
        # Safe to delete.
        obj.delete()    # removes the row from usdmast in PostgreSQL
        messages.success(request, f"User '{obj.usdusd}' deleted.")

    return redirect("user_list")
