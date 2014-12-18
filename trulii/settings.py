"""
Django settings for trulii project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import django.conf.global_settings as DEFAULT_SETTINGS


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))


#SETTINGS_PATH = os.path.realpath(os.path.dirname(__file__))

SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(7bg%ta_6%n%j76lws1h-t8s-y&4a7mr)7v39%1*y*v*te)q-='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'activities',    
    'users',
    'organizers',
    'students',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',


)




MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
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
)

ROOT_URLCONF = 'trulii.urls'

WSGI_APPLICATION = 'trulii.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'




TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


ugettext = lambda s : s
LANGUAGES = (
    ('en', ugettext('English')),
)
LOCALE_PATHS = os.path.join(BASE_DIR, 'locale')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/



#STATIC_ROOT = 
STATIC_URL = '/static/'

#STATIC_ROOT = '/static/'

STATICFILES_DIRS = (
 os.path.join(PROJECT_PATH, 'static') ,
)

from allauth_settings import *
