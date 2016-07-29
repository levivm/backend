


TAGS_MIN_OCCOURRENCE = 15

MAX_ACTIVITY_POOL_STOCK_PHOTOS = 5

MAX_ACTIVITY_PHOTOS  = 6

MAX_ACTIVITY_INSTRUCTORS = 4

#LEVEL CONTANTS
LEVEL_P = 'P'
LEVEL_I = 'I'
LEVEL_A = 'A'
LEVEL_N = 'N'


#ACTIVITY ORGANIZER STATUS
OPENED = 'opened'
CLOSED = 'closed'
UNPUBLISHED = 'unpublished'


#ACTIVITY STUDENT STATUS
CURRENT = 'current'
PAST = 'past'
NEXT = 'next'

#ACTIVITY SEARCH CONSTANTS
ORDER_MIN_PRICE = 'min_price'
ORDER_MAX_PRICE = 'max_price'
ORDER_SCORE = 'score'
ORDER_CLOSEST = 'closest'

#REQUIRED STEPS
REQUIRED_STEPS = {
    
    'general':['title','short_description','sub_category','level'],
    'calendars':['calendars'],
    'gallery':['pictures'],
    'location':['location'],

}

#ACTIViTY STEPS
ACTIVITY_STEPS = {
    
  'general':['title','short_description','sub_category','level'],
  'detail':['content', 'audience', 'goals', 'methodology', 'requirements', 'extra_info'],
  'calendars':['calendars'],
  'instructors':['instructors'],
  'location':['location'],''
  'gallery':['pictures'],
  'return_policy':['return_policy']
}
