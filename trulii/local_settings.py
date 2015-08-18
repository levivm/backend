import dj_database_url



################ DATABASE CONFIG ##############

DATABASE_URL  = "postgres://trulii:trulii@localhost:5432/trulii"
DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
################ / DATABASE CONFIG #############


################ REDIS CONFIG ##################

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost/0'
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
PAYU_TEST = True
