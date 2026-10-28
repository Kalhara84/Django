"""
Django settings for curd project.

Role of this file:
- This is the central configuration file for the entire Django project.
- It defines installed apps, database connection details, middleware, security keys,
  template configurations, and custom global variables.
"""

from pathlib import Path

# BASE_DIR represents the root directory path of this project.
# This helps construct absolute paths to other files (like sqlite DB, static files, templates).
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# Django uses this key for cryptographic signing (sessions, CSRF tokens, password reset tokens).
SECRET_KEY = 'django-insecure-68=x#^w!4nf0@3g-&a@p)6g!p569to@gd+a6382x-an)98pv(s'

# DEBUG mode: Set to True for local development to see detailed error traceback pages.
# WARNING: Must be set to False in production to avoid exposing sensitive code/server details.
DEBUG = True

# Allowed host/domain names that this Django site can serve.
# Empty list allows localhost / 127.0.0.1 in DEBUG mode.
ALLOWED_HOSTS = []


# Application definition: List of all active Django apps in this project.
INSTALLED_APPS = [
    # Built-in Django core apps:
    'django.contrib.admin',          # Built-in admin panel
    'django.contrib.auth',           # Authentication system
    'django.contrib.contenttypes',   # Tracks models installed in Django
    'django.contrib.sessions',       # Session management (stores user login state)
    'django.contrib.messages',       # Flash message framework (success/error alerts)
    'django.contrib.staticfiles',    # Manages static files (CSS, JS, images)
    
    # Custom project apps:
    'postgresql',                    # Our custom app handling user master CRUD & PostgreSQL
]

# Middleware: Functions that process every request and response globally.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',             # Basic security enhancements
    'django.contrib.sessions.middleware.SessionMiddleware',       # Enables session support across requests
    'django.middleware.common.CommonMiddleware',                 # Handles URL rewriting and common web standards
    'django.middleware.csrf.CsrfViewMiddleware',                 # Protects POST forms against Cross-Site Request Forgery
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # Associates users with requests using sessions
    'django.contrib.messages.middleware.MessageMiddleware',       # Enables flash messages across redirects
    'django.middleware.clickjacking.XFrameOptionsMiddleware',     # Prevents site from being rendered inside an iframe (clickjacking protection)
]

# Root URL configuration module where Django begins URL routing.
# Points to curd/urls.py.
ROOT_URLCONF = 'curd.urls'

# Template engine configuration: Tells Django how and where to load HTML templates.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS: Additional template folders outside apps (empty here since templates are in the app folder)
        'DIRS': [],
        # APP_DIRS: If True, Django automatically looks for a 'templates' folder inside each installed app
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Built-in context processors: inject variables into all template contexts
                'django.template.context_processors.request',          # Adds {{ request }} to templates
                'django.contrib.auth.context_processors.auth',        # Adds {{ user }} to templates
                'django.contrib.messages.context_processors.messages',# Adds {{ messages }} to templates
                
                # Custom context processor:
                # Located in curd/postgresql/context.py
                # Injects {{ APP_NAME }} and {{ usd }} into every rendered HTML template
                'postgresql.context.app_context',
            ],
        },
    },
]

# WSGI application entry point used by production web servers (like Gunicorn / uWSGI).
WSGI_APPLICATION = 'curd.wsgi.application'


# Database Configuration:
# Connects Django ORM to the PostgreSQL database server.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL database engine backend
        'NAME': 'django_test',                      # Name of the PostgreSQL database
        'USER': 'postgres',                         # Database username
        'PASSWORD': 'mypass',                       # Database password
        'HOST': 'localhost',                        # Database server host (local machine)
        'PORT': '5432',                             # Default PostgreSQL port
    }
}


# Password validation rules for Django's built-in auth system.
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


# Internationalization & Localization settings
LANGUAGE_CODE = 'en-us'            # Default language
TIME_ZONE = 'Asia/Colombo'         # Project timezone (Sri Lanka time)
USE_I18N = True                    # Enable Django's translation system
USE_TZ = True                      # Enable timezone-aware datetimes in database


# Static files (CSS, JavaScript, Images) configuration.
# The URL prefix used to serve static files in the browser (e.g. /static/css/style.css).
STATIC_URL = 'static/'

# Default auto-generated primary key field type for models (64-bit integer BigAutoField).
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---- Custom Login / Session Settings for Usdmast Table ----

# URL name to redirect unauthenticated users when they try to access protected views.
LOGIN_URL = 'login'

# Maximum session duration in seconds (14 days). Used when "Remember Me" checkbox is checked.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# Custom Application Name displayed in the login page title, sidebar header, and footer.
APP_NAME = 'JW Africa'

