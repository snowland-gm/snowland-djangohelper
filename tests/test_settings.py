# Minimal Django settings used only by the test-suite (via pytest-django).
import os
import tempfile

DB_PATH = os.path.join(tempfile.gettempdir(), 'djangohelper_test.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'rest_framework',
    'tests.testapp',
    'djangohelper.contrib.snowlandauth',
]

# Use the package's own user model so the auth backend / user relations resolve
# against SnowlandUser instead of the default auth.User.
AUTH_USER_MODEL = 'snowlandauth.SnowlandUser'

AUTHENTICATION_BACKENDS = [
    'djangohelper.contrib.snowlandauth.models.CustomBackend',
]

# The in-test app has no migrations; let Django create tables from models.
MIGRATION_MODULES = {'testapp': None}

USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECRET_KEY = 'djangohelper-test-secret-key'
