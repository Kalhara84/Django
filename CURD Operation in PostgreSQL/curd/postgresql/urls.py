# =============================================================================
# postgresql/urls.py  -  URL patterns for the postgresql app
# =============================================================================
# curd/urls.py hands ALL requests (except /admin/) to this file via include().
# This file maps each URL path to a specific view function.
#
# Views are defined in two files:
#   views.py        -> login, logout, dashboard, user CRUD
#   expire_views.py -> expire entry list / add / edit / delete
#
# How Django matches URLs:
#   The browser requests "/users/add/"
#   -> curd/urls.py sees '' prefix, delegates to this file
#   -> This file matches "users/add/"  ->  calls views.user_add
# =============================================================================

from django.urls import path

# Import view functions from the two view modules in this app.
from . import expire_views, views

urlpatterns = [
    # --- Core pages ---

    # "/"  ->  dashboard (home page after login)
    # Defined in views.py -> dashboard()
    path("", views.dashboard, name="dashboard"),

    # "/login/"  ->  login form (GET shows form, POST authenticates)
    # Defined in views.py -> login_view()
    # auth.py -> authenticate_usdmast() is called from inside login_view()
    path("login/", views.login_view, name="login"),

    # "/logout/"  ->  clears the session and redirects to /login/
    # POST only (requires_POST decorator in views.py)
    path("logout/", views.logout_view, name="logout"),

    # --- User management (admin only) ---

    # "/users/"  ->  list all users from the usdmast table
    path("users/", views.user_list, name="user_list"),

    # "/users/add/"  ->  show the add-user form / save a new user
    path("users/add/", views.user_add, name="user_add"),

    # "/users/5/edit/"  ->  edit user with primary key 5
    # <int:pk>  captures the number from the URL and passes it to the view
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),

    # "/users/5/delete/"  ->  delete user with primary key 5 (POST only)
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),

    # --- Expire module (login required, not admin-only) ---

    # "/expire/"  ->  list all expire entries (exhmast rows)
    path("expire/", expire_views.expire_list, name="expire_list"),

    # "/expire/add/"  ->  add a new expire header + lines
    path("expire/add/", expire_views.expire_add, name="expire_add"),

    # "/expire/5/edit/"  ->  edit expire entry with primary key 5
    path("expire/<int:pk>/edit/", expire_views.expire_edit, name="expire_edit"),

    # "/expire/5/delete/"  ->  delete expire entry + its lines (POST only)
    path("expire/<int:pk>/delete/", expire_views.expire_delete, name="expire_delete"),
]
