


#GENERAL CONSTANTS

#USER APP CONSTANTS

ORGANIZER_TYPE = 'O'
STUDENT_TYPE   = 'S'


#UTILS CONSTANTS


CONTENT_TYPES = ['image', 'video']

MAX_UPLOAD_PHOTO_SIZE = 2621440

#Activities APP CONSTANT

TAGS_MIN_OCCOURRENCE = 15

MAX_ACTIVITY_PHOTOS  = 6

MAX_ACTIVITY_INSTRUCTORS = 4

PREVIOUS_FIST_PUBLISH_REQUIRED_STEPS = {
    
    'general':['title','short_description','sub_category','level'],
    'calendars':['chronograms'],
    'gallery':['photos'],
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
  'gallery':['photos'],
  'return_policy':['return_policy']
}

RELATED_FIELD_REQUIREMETS = {
    
    'gallery':['photos'],

}

REQUIRED_DETAILS_STEP = ['content']

################### PAY U CONSTANTS ###################
TRANSACTION_APPROVED_CODE = '4'
TRANSACTION_DECLINED_CODE = '6'
TRANSACTION_EXPIRED_CODE  = '5'