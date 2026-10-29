# =============================================================================
# curd/settings.py - all project settings
# =============================================================================
# Important parts:
#   INSTALLED_APPS      -> our app "postgresql" is registered here
#   TEMPLATES           -> adds postgresql/context.py to every page
#   DATABASES           -> PostgreSQL connection (change the name/password for your PC)
#   LOGIN_URL / SESSION -> used by postgresql/decorators.py and views.py
# =============================================================================
from pathlib import Path

# Project root folder (the folder that has manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key used for sessions and CSRF. Keep it secret in production.
SECRET_KEY = 'django-insecure-68=x#^w!4nf0@3g-&a@p)6g!p569to@gd+a6382x-an)98pv(s'

# DEBUG = True shows detailed errors. Set False in production.
DEBUG = True

# Host names allowed to open the site ('*' = any)
ALLOWED_HOSTS = ['*']

# Apps used by this project
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',      # login session (used in postgresql/views.py)
    'django.contrib.messages',      # green/red alert messages
    'django.contrib.staticfiles',   # css, js, images

    # Our app (models, views, templates, static files)
    'postgresql',
]

# Middleware = code that runs on every request/response
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',          # checks {% csrf_token %} in forms
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Main URL file -> curd/urls.py
ROOT_URLCONF = 'curd.urls'

# Where Django finds HTML templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # No extra folders; templates are inside postgresql/templates/
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Variables that every template can use
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Ours: gives {{ APP_NAME }} and {{ usd }} (logged user), see postgresql/context.py
                'postgresql.context.app_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'curd.wsgi.application'

# PostgreSQL connection. Change NAME / USER / PASSWORD to match your PC.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_test',
        'USER': 'postgres',
        'PASSWORD': 'mypass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Rules for Django's own password checking (not used by our usdmast login)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Language and time zone (audit date/time columns use this time zone)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Colombo'
USE_I18N = True
USE_TZ = True

# URL prefix for css/js/images (files are in postgresql/static/)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---- Our own settings -------------------------------------------------------
# Not logged in -> redirect to the page named "login" (postgresql/urls.py)
LOGIN_URL = 'login'

# "Remember me" keeps the login for 14 days (set in postgresql/views.py)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# Name shown on the login page and sidebar
APP_NAME = 'JW Africa'
