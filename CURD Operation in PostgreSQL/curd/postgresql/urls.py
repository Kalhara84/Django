"""
URL Configuration for 'postgresql' app.

Role of this file:
- Maps URL path patterns to corresponding view controller functions in views.py.
- Included by the project's root URLconf (curd/urls.py).
- Each route has a unique 'name' attribute used for reverse URL resolution in templates
  (e.g., {% url 'dashboard' %}) and redirects in Python code (e.g., redirect('user_list')).
"""

from django.urls import path

from . import views

urlpatterns = [
    # Dashboard route: / (root home page of app)
    path("", views.dashboard, name="dashboard"),
    
    # Authentication routes:
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # User Master CRUD routes:
    path("users/", views.user_list, name="user_list"),                        # Read (List users)
    path("users/add/", views.user_add, name="user_add"),                      # Create (Add user)
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),          # Update (Edit user by ID)
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),    # Delete (Delete user by ID)
]

