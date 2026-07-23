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
    'rest_framework',
    'tests.testapp',
]

# The in-test app has no migrations; let Django create tables from models.
MIGRATION_MODULES = {'testapp': None}

USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECRET_KEY = 'djangohelper-test-secret-key'
