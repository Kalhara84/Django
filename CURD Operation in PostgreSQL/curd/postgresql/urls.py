from django.urls import path

from . import expire_views, views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.user_add, name="user_add"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),

    # Expire module
    path("expire/", expire_views.expire_list, name="expire_list"),
    path("expire/add/", expire_views.expire_add, name="expire_add"),
    path("expire/<int:pk>/edit/", expire_views.expire_edit, name="expire_edit"),
    path("expire/<int:pk>/delete/", expire_views.expire_delete, name="expire_delete"),
]
