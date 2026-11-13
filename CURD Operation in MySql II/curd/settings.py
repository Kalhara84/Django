# =============================================================================
# curd/settings.py - all project settings
# =============================================================================
# Important parts:
#   INSTALLED_APPS      -> our app "postgresql" is registered here
#   TEMPLATES           -> adds postgresql/context.py to every page
#   DATABASES           -> MySQL connection (values are read from the .env file)
#   LOGIN_URL / SESSION -> used by postgresql/decorators.py and views.py
# =============================================================================
import os
from pathlib import Path

from dotenv import load_dotenv

# Project root folder (the folder that has manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Read secrets (passwords, keys) from the .env file in the project root.
# .env is NOT uploaded to git - copy .env.example to .env and fill your values.
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    # Turns .env text like True/1/yes into a real True/False
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')

# Secret key used for sessions and CSRF. Keep it secret in production.
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me')

# DEBUG = True shows detailed errors. Set False in production.
DEBUG = env_bool('DEBUG', True)

# Host names allowed to open the site ('*' = any)
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '*').split(',') if h.strip()]

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
    # WhiteNoise serves css/js/images even when DEBUG=False (needed on a real server)
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

# MySQL connection. All values come from the .env file (see .env.example).
# (Create the database first: CREATE DATABASE django_test CHARACTER SET utf8mb4;)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', ''),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            # Strict mode: MySQL rejects wrong values instead of silently changing them
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Cloud MySQL (like Aiven) needs an SSL connection. PyMySQL only uses SSL when told to.
#   DB_SSL_CA=path/to/ca.pem -> SSL with certificate check (best)
#   DB_SSL=True              -> SSL without certificate check (quick option)
_db_ssl_ca = os.getenv('DB_SSL_CA', '').strip()
if _db_ssl_ca:
    DATABASES['default']['OPTIONS']['ssl'] = {'ca': str(BASE_DIR / _db_ssl_ca)}
elif env_bool('DB_SSL', False):
    DATABASES['default']['OPTIONS']['ssl'] = {'ca': None}

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

# "python manage.py collectstatic" copies all static files here.
# WhiteNoise then serves them in production (DEBUG=False).
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Needed when the site runs on a https domain (comma separated), e.g. https://mysite.com
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---- Our own settings -------------------------------------------------------
# Not logged in -> redirect to the page named "login" (postgresql/urls.py)
LOGIN_URL = 'login'

# "Remember me" keeps the login for 14 days (set in postgresql/views.py)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# Name shown on the login page and sidebar
APP_NAME = 'JW Africa'
