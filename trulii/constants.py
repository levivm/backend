


#GENERAL CONSTANTS

#USER APP CONSTANTS

ORGANIZER_TYPE = 'O'
STUDENT_TYPE   = 'S'

STUDENT_PERMISSIONS = (
    {
        'app': 'orders',
        'model': 'order',
        'codenames': ('add',),
    },
    {
        'app': 'orders',
        'model': 'assistant',
        'codenames': ('add',),
    },
    {
        'app': 'students',
        'model': 'student',
        'codenames': ('change',),
    },
    {
        'app': 'reviews',
        'model': 'review',
        'codenames': ('add',),
    },
)

ORGANIZER_PERMISSIONS = (
    {
        'app': 'activities',
        'model': 'tags',
        'codenames': ('add',),
    },
    {
        'app': 'activities',
        'model': 'activity',
        'codenames': ('add', 'change'),
    },
    {
        'app': 'activities',
        'model': 'activityphoto',
        'codenames': ('add', 'delete'),
    },
    {
        'app': 'activities',
        'model': 'chronogram',
        'codenames': ('add', 'change', 'delete'),
    },
    {
        'app': 'activities',
        'model': 'session',
        'codenames': ('add', 'change', 'delete'),
    },
    {
        'app': 'locations',
        'model': 'location',
        'codenames': ('add', 'change', 'delete'),
    },
    {
        'app': 'organizers',
        'model': 'organizer',
        'codenames': ('change',),
    },
    {
        'app': 'organizers',
        'model': 'instructor',
        'codenames': ('add', 'change', 'delete'),
    },
    {
        'app': 'reviews',
        'model': 'review',
        'codenames': ('change',),
    },
)


#UTILS CONSTANTS


CONTENT_TYPES = ['image', 'video']

MAX_UPLOAD_PHOTO_SIZE = 2621440

#Activities APP CONSTANT

TAGS_MIN_OCCOURRENCE = 15

MAX_ACTIVITY_POOL_STOCK_PHOTOS = 5

MAX_ACTIVITY_PHOTOS  = 6

MAX_ACTIVITY_INSTRUCTORS = 4

PREVIOUS_FIST_PUBLISH_REQUIRED_STEPS = {
    
    'general':['title','short_description','sub_category','level'],
    'calendars':['chronograms'],
    'gallery':['pictures'],
    'location':['location'],

}

REQUIRED_STEPS = {
    
    'general':['title','short_description','sub_category','level'],
    'location':['location'],

}

ACTIVITY_STEPS = {
    
  'general':['title','short_description','sub_category','level'],
  'detail':['content', 'audience', 'goals', 'methodology', 'requirements', 'extra_info'],
  'calendars':['chronograms'],
  'instructors':['instructors'],
  'location':['location'],''
  'gallery':['pictures'],
  'return_policy':['return_policy']
}

RELATED_FIELD_REQUIREMETS = {
    
    'gallery':['pictures'],

}

REQUIRED_DETAILS_STEP = ['content']

################### PAY U CONSTANTS ###################
TRANSACTION_APPROVED_CODE = '4'
TRANSACTION_DECLINED_CODE = '6'
TRANSACTION_EXPIRED_CODE  = '5'