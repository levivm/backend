import logging
from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'HOST': '',
        'NAME': ':memory:',
        'PASSWORD': '',
        'PORT': '',
        'USER': '',
        'TEST': {
            'NAME': 'test_trulii_db'
        }
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

DEBUG = False
TEMPLATE_DEBUG = False

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'
BROKER_URL = 'memory://localhost'

logging.disable(logging.CRITICAL)
