


#GENERAL CONSTANTS

FRONT_SERVER_URL = "http://localhost:8080"


#USER APP CONSTANTS

ORGANIZER_TYPE = 'O'
STUDENT_TYPE   = 'S'


#UTILS CONSTANTS


CONTENT_TYPES = ['image', 'video']

MAX_UPLOAD_PHOTO_SIZE = 2621440

#Activities APP CONSTANT

TAGS_MIN_OCCOURRENCE = 15

MAX_ACTIVITY_PHOTOS  = 6

STEPS_REQUIREMENTS = {
	
	'general':['title','short_description','large_description','sub_category_id','level','type'],
	'detail':['content'],
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