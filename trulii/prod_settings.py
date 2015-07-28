import os
import dj_database_url


################ DATABASE CONFIG ##############

# DATABASE_URL  = "postgres://trulii:trulii@localhost:5432/trulii"

DATABASE_URL  = os.environ.get('RDS_DATABASE_URL')
DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

################ / DATABASE CONFIG #############




################ REDIS CONFIG ##################

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost/0'
CELERY_ALWAYS_EAGER = False 


################ / REDIS CONFIG #################

FRONT_SERVER_URL = "https://dev.trulii.com/"