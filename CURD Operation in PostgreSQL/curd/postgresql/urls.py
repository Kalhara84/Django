# =============================================================================
# postgresql/urls.py - page addresses of our app
# =============================================================================
# Included from curd/urls.py.
#   views.py        -> login, dashboard, users
#   expire_views.py -> Expire Module
# The "name" is used in templates, e.g. {% url 'expire_list' %}.
# =============================================================================
from django.urls import path

from . import expire_views, views

urlpatterns = [
    # Dashboard (home)
    path("", views.dashboard, name="dashboard"),

    # Login / logout
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Users tab
    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.user_add, name="user_add"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),

    # Expire Module tab
    path("expire/", expire_views.expire_list, name="expire_list"),
    path("expire/add/", expire_views.expire_add, name="expire_add"),
    path("expire/<int:pk>/edit/", expire_views.expire_edit, name="expire_edit"),
    path("expire/<int:pk>/delete/", expire_views.expire_delete, name="expire_delete"),

    # "Add Location" pop-up on the Expire form (called by expire-form.js)
    path("expire/location/add/", expire_views.location_add, name="expire_location_add"),
]
