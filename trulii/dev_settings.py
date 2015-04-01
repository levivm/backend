import dj_database_url
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
################AMAZON S3 STORAGE ##########################


AWS_STORAGE_BUCKET_NAME = 'trulii-dev'
AWS_ACCESS_KEY_ID = 'AKIAJRUNNQDO2LM6OSEA'
AWS_SECRET_ACCESS_KEY = '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'


# Tell django-storages that when coming up with the URL for an item in S3 storage, keep
# it simple - just use this domain plus the path. (If this isn't set, things get complicated).
# This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
# We also use it in the next setting.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False


###STATIC#####



# This is used by the `static` template tag from `static`, if you're using that. Or if anything else
# refers directly to STATIC_URL. So it's safest to always set it.

# Tell the staticfiles app to use S3Boto storage when writing the collected static files (when
# you run `collectstatic`).
#STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# STATICFILES_LOCATION = 'static'
# STATICFILES_STORAGE  = 'trulii.custom_storages.StaticRootS3BotoStorage'
# STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

########MEDIA##########


#
DATABASES = {}
DATABASES['default'] = dj_database_url.config()



############################################################