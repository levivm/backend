


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
        'codenames': ('add', 'change', 'delete'),
    },
    {
        'app': 'activities',
        'model': 'activityphoto',
        'codenames': ('add', 'delete'),
    },
    {
        'app': 'activities',
        'model': 'calendar',
        'codenames': ('add', 'change', 'delete'),
    },
    {
        'app': 'activities',
        'model': 'calendarsession',
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
    {
        'app': 'organizers',
        'model': 'organizerbankinfo',
        'codenames': ('add', 'change'),
    },
    {
        'app': 'trulii_messages',
        'model': 'organizermessage',
        'codenames': ('add',)
    }
)

OPERATIVE_PERMISSIONS = (
    {
        'app': 'activities',
        'model': 'activityphoto',
        'codenames': ['add', 'change'],
    },
    {
        'app': 'activities',
        'model': 'activitystockphoto',
        'codenames': ['add', 'change'],
    },
    {
        'app': 'activities',
        'model': 'activity',
        'codenames': ['change'],
    },
    {
        'app': 'activities',
        'model': 'calendarsession',
        'codenames': ['change'],
    },
    {
        'app': 'activities',
        'model': 'calendar',
        'codenames': ['change'],
    },
    {
        'app': 'activities',
        'model': 'category',
        'codenames': ['change'],
    },
    {
        'app': 'activities',
        'model': 'subcategory',
        'codenames': ['change'],
    },
    {
        'app': 'activities',
        'model': 'tags',
        'codenames': ['add','change', 'delete'],
    },
    {
        'app': 'locations',
        'model': 'city',
        'codenames': ['change'],
    },
    {
        'app': 'locations',
        'model': 'location',
        'codenames': ['add', 'change'],
    },
    {
        'app': 'orders',
        'model': 'assistant',
        'codenames': ['change'],
    },
    {
        'app': 'orders',
        'model': 'order',
        'codenames': ['change'],
    },
    {
        'app': 'organizers',
        'model': 'instructor',
        'codenames': ['add','change', 'delete'],
    },
    {
        'app': 'organizers',
        'model': 'organizerbankinfo',
        'codenames': ['add', 'change'],
    },
    {
        'app': 'organizers',
        'model': 'organizer',
        'codenames': ['change'],
    },
    {
        'app': 'payments',
        'model': 'fee',
        'codenames': ['change'],
    },
    {
        'app': 'payments',
        'model': 'payment',
        'codenames': ['change'],
    },
    {
        'app': 'referrals',
        'model': 'coupontype',
        'codenames': ['change'],
    },
    {
        'app': 'referrals',
        'model': 'coupon',
        'codenames': ['change'],
    },
    {
        'app': 'referrals',
        'model': 'referral',
        'codenames': ['change'],
    },
    {
        'app': 'referrals',
        'model': 'redeem',
        'codenames': ['change'],
    },
    {
        'app': 'reviews',
        'model': 'review',
        'codenames': ['change'],
    },
    {
        'app': 'students',
        'model': 'student',
        'codenames': ['change'],
    },
    {
        'app': 'users',
        'model': 'organizerconfirmation',
        'codenames': ['change'],
    },
    {
        'app': 'users',
        'model': 'requestsignup',
        'codenames': ['change'],
    },
    {
        'app': 'utils',
        'model': 'emailtaskrecord',
        'codenames': ['change'],
    },
)


#UTILS CONSTANTS


CONTENT_TYPES = ['image', 'video']

MAX_UPLOAD_PHOTO_SIZE = 2621440

#CALENDAR APP CONSTANT

MIN_ALLOWED_CALENDAR_PRICE = 30000



#SEARCH APP CONSTANT

PRICE_RANGE = {
    'max':1000000,
    'min':30000,
    'step':50000
}


#ACTIVITIES APP CONSTANT

TAGS_MIN_OCCOURRENCE = 15

MAX_ACTIVITY_POOL_STOCK_PHOTOS = 5

MAX_ACTIVITY_PHOTOS  = 6

MAX_ACTIVITY_INSTRUCTORS = 4

PREVIOUS_FIST_PUBLISH_REQUIRED_STEPS = {
    
    'general':['title','short_description','sub_category','level'],
    'calendars':['calendars'],
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
  'calendars':['calendars'],
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
TRANSACTION_PENDING_PSE_CODE  = '12'
RESPONSE_CODE_POL_FAILED = '5'
RESPONSE_CODE_POL_DECLINED = '4'
PSE_METHOD_PAYMENT_ID = '4'
CC_METHOD_PAYMENT_ID  = '2'
