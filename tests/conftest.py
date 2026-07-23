# Ensure the project root is importable so `tests.test_settings` and
# `djangohelper` can be imported. Django itself is configured by pytest-django
# via the DJANGO_SETTINGS_MODULE in pytest.ini.
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
