import logging
from .base import *


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'HOST': '',
#         'NAME': ':memory:',
#         'PASSWORD': '',
#         'PORT': '',
#         'USER': '',
#         'TEST': {
#             'NAME': 'test_trulii_db'
#         }
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'localhost',
        'NAME': 'trulii_test',
        'PASSWORD': '',
        'PORT': '5432',
        'USER': 'trulii',
    }
}

del MEDIAFILES_LOCATION
del DEFAULT_FILE_STORAGE

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
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'memory'
BROKER_BACKEND = 'memory'
BROKER_URL = 'memory://localhost'

FRONT_SERVER_URL = "http://localhost:8080/"

PAYU_API_KEY = '6u39nqhq8ftd0hlvnjfs66eh8c'
PAYU_MERCHANT_ID = '500238'
PAYU_API_LOGIN = '11959c415b33d0c'
PAYU_ACCOUNT_ID = '500538'
PAYU_URL = 'http://stg.api.payulatam.com/payments-api/4.0/service.cgi'
PAYU_NOTIFY_URL = "https://api.trulii.com/api/payments/notification"
PAYU_RESPONSE_URL = "https://api.trulii.com/api/payments/pse/response"
PAYU_TEST = True
PAYU_TEST_TOKEN = 'eyJ0b2tlbiI6ImEyMDA0NmU3LWZjOTktNDc3OS04ZGQ3LTA'
PAYU_TEST_TOKEN += 'zMzE1ZjBjY2VhMSJ9:1aJ6Yo:OkyLEE5T'
PAYU_TEST_TOKEN += '-ZaaPxl7fSAVuH9YVog'

MANDRILL_API_KEY = 'm4ndr1ll_4p1_k3y'

logging.disable(logging.CRITICAL)
