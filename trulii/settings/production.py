import os
import dj_database_url
from distutils import util

from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

################ DATABASE CONFIG ##############

# DATABASE_URL  = "postgres://trulii:trulii@localhost:5432/trulii"

DATABASE_URL  = os.environ.get('RDS_DATABASE_URL')
DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

################ / DATABASE CONFIG #############


STATICFILES_STORAGE = 'trulii.custom_storages.StaticRootS3BotoStorage'


################ REDIS CONFIG ##################


REDIS_HOST_ADDR = "redis"
REDIS_PORT = "6379"

BROKER_URL = 'redis://{host}:{port}/0'.format(host=REDIS_HOST_ADDR, port=REDIS_PORT)
CELERY_RESULT_BACKEND = 'redis://{host}/0'.format(host=REDIS_HOST_ADDR)
CELERY_ALWAYS_EAGER = False


################  RAVEN CONFIG #################

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN')
    # If you are using git, you can also automatically configure the
    # release based on the git info.
}


# SET DOMAINS
CSRF_COOKIE_DOMAIN = '.trulii.com'
SESSION_COOKIE_DOMAIN = '.trulii.com'



################ SENDGRID #######################
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')


################ / REDIS CONFIG #################

FRONT_SERVER_URL = os.environ.get('FRONT_SERVER_URL')

# Pay U configuration
PAYU_API_KEY = os.environ.get('PAYU_API_KEY')
PAYU_MERCHANT_ID = os.environ.get('PAYU_MERCHANT_ID')
PAYU_ACCOUNT_ID = os.environ.get('PAYU_ACCOUNT_ID')
PAYU_API_LOGIN = os.environ.get('PAYU_API_LOGIN')
PAYU_URL = os.environ.get('PAYU_URL')
PAYU_TEST = util.strtobool(os.environ.get('PAYU_TEST', 'false'))
PAYU_NOTIFY_URL = os.environ.get('PAYU_NOTIFY_URL')
PAYU_RESPONSE_URL = os.environ.get('PAYU_RESPONSE_URL')

# Social Auth
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'publish_stream']
SOCIAL_AUTH_FACEBOOK_REDIRECT_URI = os.environ.get('SOCIAL_AUTH_FACEBOOK_REDIRECT_URI')

#################### LOGGIN ########################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'INFO', # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
    },
    'loggers': {
        'payment': {
            'level': 'INFO',
            'handlers': ['sentry'],
            'propagate': False
        },
    },
}
