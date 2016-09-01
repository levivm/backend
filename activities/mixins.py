from rest_framework import serializers

from activities.tasks import ActivityScoreTask
from students.models import Student, WishList


class ActivityMixin(object):
    select_related_fields = ['organizer__user', 'sub_category__category', 'location__city']
    prefetch_related_fields = ['pictures',
                               'calendars__orders__student__user',
                               'calendars__orders__assistants']

    def calculate_score(self, activity_id):
        task = ActivityScoreTask()
        task.delay(activity_id)


class ActivityCardMixin(object):
    select_related_fields = ['organizer', 'sub_category__category']
    prefetch_related_fields = ['pictures']


class WishListSerializerMixin(serializers.Serializer):
    wish_list = serializers.SerializerMethodField()

    def get_wish_list(self, obj):
        request = self.context.get('request')
        if request:
            try:
                profile = request.user.get_profile()
            except AttributeError:
                return False

            if isinstance(profile, Student):
                return WishList.objects.filter(student=profile, activity=obj).exists()

        return False
