
import os
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))


STATIC_URL = '/static/'
STATICFILES_DIRS = (
 os.path.join(PROJECT_PATH, 'static') ,
)