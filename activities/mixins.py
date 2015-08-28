from activities.tasks import ActivityScoreTask


class CalculateActivityScoreMixin(object):
    def calculate_score(self, activity_id):
        task = ActivityScoreTask()
        task.delay(activity_id)
