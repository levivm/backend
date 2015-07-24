"""
Django settings for trulii project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import django.conf.global_settings as DEFAULT_SETTINGS
# import dj_database_url
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

IS_PRODUCTION = os.environ.get('PRODUCTION_SERVER')
print(os.environ)
print("12213122122")
print(os.environ)
print(os.environ)
print(os.environ.get('PRODUCTION_SERVER'))
print(os.environ.get('PRODUCTION_SERVER'))

DEBUG = True if not IS_PRODUCTION else False



SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(7bg%ta_6%n%j76lws1h-t8s-y&4a7mr)7v39%1*y*v*te)q-='

# SECURITY WARNING: don't run with debug turned on in production!





REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}

ANONYMOUS_USER_ID = -1

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'storages',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'landing',
    'activities',
    'locations',    
    'users',
    'organizers',
    'students',
    'allauth',
    'utils',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'orders',
    'guardian',
)




MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS =  DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    "django.core.context_processors.request",
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
    
)


TEMPLATE_DIRS = DEFAULT_SETTINGS.TEMPLATE_DIRS + (
    PROJECT_PATH + '/templates/', 
)
#TEMPLATES_PATH = os.path.join(SETTINGS_PATH, "templates")


AUTHENTICATION_BACKENDS = DEFAULT_SETTINGS.AUTHENTICATION_BACKENDS + ( 

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
    'guardian.backends.ObjectPermissionBackend',
)

ROOT_URLCONF = 'trulii.urls'

WSGI_APPLICATION = 'trulii.wsgi.application'


#---------CORS SETTINGS------------
#CORS_URLS_REGEX = r'^/api/.*$'

CORS_ORIGIN_ALLOW_ALL = True



EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

#LANGUAGE_CODE = 'en-us'




# TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


ugettext = lambda s : s
LANGUAGE_CODE = 'es-ES'
LANGUAGES = (
    #('en', ugettext('English')),
    ('es', ugettext('Spanish')),
)
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/




AWS_STORAGE_BUCKET_NAME = 'trulii-dev'
AWS_ACCESS_KEY_ID = 'AKIAJRUNNQDO2LM6OSEA'
AWS_SECRET_ACCESS_KEY = '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'
# Tell django-storages that when coming up with the URL for an item in S3 storage, keep
# it simple - just use this domain plus the path. (If this isn't set, things get complicated).
# This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
# We also use it in the next setting.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False


MEDIAFILES_LOCATION = 'media' 
DEFAULT_FILE_STORAGE = 'trulii.custom_storages.MediaRootS3BotoStorage'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)


STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, "static"),
)

STATIC_ROOT = os.path.join(PROJECT_PATH, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT  = os.path.join(PROJECT_PATH, 'media')

if not DEBUG:
    from .prod_settings import *
    # DEBUG = True
else:
    from .local_settings import *


from .allauth_settings import *
from .constants import *