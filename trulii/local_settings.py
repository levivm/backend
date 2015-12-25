import dj_database_url
import os



################ DATABASE CONFIG ##############

DATABASE_URL  = "postgres://trulii:trulii@localhost:5432/trulii"
DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
################ / DATABASE CONFIG #############


################ REDIS CONFIG ##################
REDIS_HOST_ADDR = os.environ.get('REDIS_1_PORT_6379_TCP_ADDR','localhost')
REDIS_PORT = os.environ.get('REDIS_1_PORT_6379_TCP_PORT','6379')

# BROKER_URL = 'redis://localhost:6379/0'
BROKER_URL = 'redis://{host}:{port}/0'.format(host=REDIS_HOST_ADDR, port=REDIS_PORT)
CELERY_RESULT_BACKEND = 'redis://{host}/0'.format(host=REDIS_HOST_ADDR)
CELERY_ALWAYS_EAGER = False

################ / REDIS CONFIG #################

FRONT_SERVER_URL = "http://localhost:8080/"

############### PayU ###########################
PAYU_API_KEY = '6u39nqhq8ftd0hlvnjfs66eh8c'
PAYU_MERCHANT_ID = '500238'
PAYU_API_LOGIN = '11959c415b33d0c'
PAYU_ACCOUNT_ID = '500538'
PAYU_URL = 'http://stg.api.payulatam.com/payments-api/4.0/service.cgi'
PAYU_NOTIFY_URL = "https://api.trulii.com/api/payments/notification"
PAYU_RESPONSE_URL = "https://api.trulii.com/api/payments/pse/response"
PAYU_TEST = True
