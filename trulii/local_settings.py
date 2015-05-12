import dj_database_url
import os
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#STATIC_ROOT = os.path.join(PROJECT_PATH, 'staticfiles')


# DATABASES = {}
# DATABASES['default'] = dj_database_url.config()
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'trulii',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'trulii',
        'PASSWORD': 'trulii',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}


BROKER_URL = 'redis://localhost:6379/0'
