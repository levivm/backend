from activities.tasks import ActivityScoreTask


class ActivityMixin(object):
    select_related_fields = ['organizer__user', 'sub_category__category', 'location__city']
    prefetch_related_fields = ['pictures', 'calendars__sessions',
                               'calendars__orders__refunds',
                               'calendars__orders__student__user',
                               'calendars__orders__assistants__refunds']


    def calculate_score(self, activity_id):
        task = ActivityScoreTask()
        task.delay(activity_id)


class ActivityCardMixin(object):
    select_related_fields = ['organizer', 'sub_category__category']
    prefetch_related_fields = ['pictures', 'calendars__sessions']
