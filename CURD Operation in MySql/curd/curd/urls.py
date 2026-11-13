# =============================================================================
# curd/urls.py - main URL list of the project
# =============================================================================
# Django checks this file first (ROOT_URLCONF in settings.py).
# Every page URL of our app is in postgresql/urls.py and is added here with include().
# =============================================================================
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    # Browser asks for /favicon.ico -> send it our logo
    path('favicon.ico', RedirectView.as_view(url='/static/assesst/img/jw-logo.svg', permanent=True)),

    # Django admin site (/admin/)
    path('admin/', admin.site.urls),

    # All other pages (login, dashboard, users, expire) -> postgresql/urls.py
    path('', include('postgresql.urls')),
]
