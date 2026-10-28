# =============================================================================
# curd/urls.py  -  Root URL configuration (the main "switchboard")
# =============================================================================
# Django reads this file to figure out which view function to call for each
# incoming URL.  This is the top-level router; it delegates most work to the
# postgresql app's own urls.py via include().
#
# Flow:
#   Browser sends URL
#     -> Django checks this file (ROOT_URLCONF = 'curd.urls' in settings.py)
#     -> Matches a pattern
#     -> Calls the matching view function
# =============================================================================

from django.contrib import admin       # Django's built-in admin site
from django.urls import include, path  # helpers to build URL patterns
from django.views.generic.base import RedirectView  # helper to redirect URLs

urlpatterns = [
    # Favicon route to prevent 404 in browser console
    path('favicon.ico', RedirectView.as_view(url='/static/assesst/img/jw-logo.svg', permanent=True)),

    # /admin/  ->  Django's built-in admin interface (login, manage DB records)
    path('admin/', admin.site.urls),

    # ''  (empty string = the site root "/")
    # ->  hand ALL other URLs to postgresql/urls.py for further routing.
    # include() reads postgresql/urls.py and tries each pattern there.
    path('', include('postgresql.urls')),
]
