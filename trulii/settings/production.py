import os
import dj_database_url

from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

################ DATABASE CONFIG ##############

# DATABASE_URL  = "postgres://trulii:trulii@localhost:5432/trulii"

DATABASE_URL  = os.environ.get('RDS_DATABASE_URL')
DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

################ / DATABASE CONFIG #############




################ REDIS CONFIG ##################


REDIS_HOST_ADDR = os.environ.get('REDIS_1_PORT_6379_TCP_ADDR','localhost')
REDIS_PORT = os.environ.get('REDIS_1_PORT_6379_TCP_PORT','6379')

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



################ SENDGRID #######################
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')


################ / REDIS CONFIG #################

FRONT_SERVER_URL = "https://dev.trulii.com/"
PAYU_API_KEY = '6RK49XdJYozqO05lnIJQonnbEx'
PAYU_MERCHANT_ID = '537033'
PAYU_ACCOUNT_ID = '539061'
PAYU_API_LOGIN = 'xvoZMctc645I2Nc'
PAYU_URL = 'https://api.payulatam.com/payments-api/4.0/service.cgi'
PAYU_TEST = False
PAYU_NOTIFY_URL = "https://api.trulii.com/api/payments/notification"
PAYU_RESPONSE_URL = "https://dev.trulii.com/payments/pse/response"