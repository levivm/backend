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

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost/0'
CELERY_ALWAYS_EAGER = False 

################ SENDGRID #######################
SENDGRID_API_KEY = "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"



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