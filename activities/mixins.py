import pymongo
from django.conf import settings
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


class MongoMixin(object):

    def __init__(self):
        self.client = self._get_client()
        self.db = self.client.trulii

    def _get_client(self):
        return pymongo.MongoClient(settings.MONGO_URL)

    def get_collection(self, name):
        return self.db[name]
