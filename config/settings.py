# safe-odds/config/settings.py
"""
Django settings for the Safe Odds project.

Quick explanation for learning Django:
- This file is the central configuration for the entire project.
- It tells Django which apps to use, how to connect to the database,
  where to find templates and static files, and security settings.
- Values marked os.environ.get(...) are read from your .env file,
  keeping secrets out of the code.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR points to the root folder of the project (where manage.py lives).
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Safety net: Render sets the RENDER environment variable on its platform.
# Never run in debug on Render, even if DEBUG was accidentally left as True.
if os.environ.get('RENDER'):
    DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
# In development a throwaway key is fine, but in production (DEBUG=False) the
# key MUST come from the environment so a real secret is never committed.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-key-change-in-production'
    else:
        raise ImproperlyConfigured(
            'The SECRET_KEY environment variable must be set when DEBUG is False.'
        )

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
    if h.strip()
]

# If deployed on Render, automatically allow the Render hostname
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Trusted origins for CSRF (required for the HTTPS admin/forms on Render).
# Set CSRF_TRUSTED_ORIGINS in the environment as a comma-separated list.
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if o.strip()
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


# Application definition
# Each entry here is a Django "app" — a self-contained module with its own
# models, views, and templates. Django comes with several built-in apps
# (admin, auth, etc.) and we add our own ('matches') below.

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Our apps
    'matches',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Reads DATABASE_URL from the environment (Supabase Postgres in production),
# falling back to local SQLite when it is not set (local development).
#
# Supabase connection strings:
#   - Session pooler (port 5432) — recommended for Render (works over IPv4).
#   - Transaction pooler (port 6543) — needs server-side cursors disabled.

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# The Supabase transaction pooler (port 6543) does not support server-side
# cursors, so disable them automatically when that port is in use.
if DATABASES['default'].get('ENGINE') == 'django.db.backends.postgresql':
    if str(DATABASES['default'].get('PORT')) == '6543':
        DATABASES['default'].setdefault('OPTIONS', {})
        DATABASES['default']['OPTIONS']['DISABLE_SERVER_SIDE_CURSORS'] = True

# The test suite always runs on local SQLite so tests never touch the
# production Postgres database configured in DATABASE_URL.
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'

# Store all times in UTC in the database.
# We'll convert to WAT/EST when displaying to visitors.
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, images)
# STATIC_URL is the web address prefix for static files.
# STATIC_ROOT is where collectstatic gathers them for production.

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise serves compressed, cache-busted static files in production.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'config.storage.CompressedManifestStaticFilesStorage',
    },
}


# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Custom project settings ---

# SportyBet affiliate URL (shown on bet buttons)
SPORTYBET_URL = os.environ.get('SPORTYBET_URL', 'https://www.sportybet.com')


# --- Production security (only enforced when DEBUG is False) ---
if not DEBUG:
    # Trust Render's proxy header so Django knows the request was HTTPS.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
