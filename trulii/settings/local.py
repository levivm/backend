import dj_database_url

from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS += (
    'debug_toolbar',
)

# DATABASE CONFIG

POSTGRES_PORT = os.environ.get('POSTGRES_PORT_5432_TCP_PORT', '5432')
POSTGRES_HOST = os.environ.get('POSTGRES_PORT_5432_TCP_ADDR', 'localhost')

PG_USER = os.environ.get('POSTGRES_1_ENV_POSTGRES_USER', 'trulii')
PG_DB = os.environ.get('POSTGRES_1_ENV_POSTGRES_DB', 'trulii')
PG_PW = os.environ.get('POSTGRES_1_ENV_POSTGRES_PASSWORD', 'trulii')

DATABASE_URL = "postgis://{user}:{password}@{host}:{port}/{db}".format(host=POSTGRES_HOST,
                                                                       port=POSTGRES_PORT,
                                                                       db=PG_DB, user=PG_USER,
                                                                       password=PG_PW)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

LOGGING_CONFIG = {}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'localhost:11211',
#     }
# }

# REDIS CONFIG
REDIS_HOST_ADDR = os.environ.get('REDIS_1_PORT_6379_TCP_ADDR', 'localhost')
REDIS_PORT = os.environ.get('REDIS_1_PORT_6379_TCP_PORT', '6379')

# BROKER_URL = 'redis://localhost:6379/0'
BROKER_URL = 'redis://{host}:{port}/0'.format(host=REDIS_HOST_ADDR, port=REDIS_PORT)
CELERY_RESULT_BACKEND = 'redis://{host}/0'.format(host=REDIS_HOST_ADDR)
CELERY_ALWAYS_EAGER = False

FRONT_SERVER_URL = "http://localhost:8080/"

# PayU
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

# SendGrid
SENDGRID_API_KEY = "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"

# Social Auth
SOCIAL_AUTH_FACEBOOK_KEY = '1701354690078591'
SOCIAL_AUTH_FACEBOOK_SECRET = '50b6017d2f21dc898fad2fc23f23cf44'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'publish_stream']
SOCIAL_AUTH_FACEBOOK_REDIRECT_URI = 'http://trulii.com/home'
