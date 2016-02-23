from activities.tasks import ActivityScoreTask


class ActivityMixin(object):

    def calculate_score(self, activity_id):
        task = ActivityScoreTask()
        task.delay(activity_id)


class ActivityCardMixin(object):
    select_related_fields = ['organizer', 'sub_category__category']
    prefetch_related_fields = ['pictures', 'calendars__sessions']
