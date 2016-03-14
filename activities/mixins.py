from itertools import filterfalse

from rest_framework import serializers

from activities.tasks import ActivityScoreTask
from students.models import Student, WishList


class CalculateActivityScoreMixin(object):
    def calculate_score(self, activity_id):
        task = ActivityScoreTask()
        task.delay(activity_id)


class ListUniqueOrderedElementsMixin(object):
    @staticmethod
    def unique_everseen(iterable, key=None):
        "List unique elements, preserving order. Remember all elements ever seen."
        # unique_everseen('AAAABBBCCDAABBB') --> A B C D
        # unique_everseen('ABBCcAD', str.lower) --> A B C D
        seen = set()
        seen_add = seen.add
        if key is None:
            for element in filterfalse(seen.__contains__, iterable):
                seen_add(element)
                yield element
        else:
            for element in iterable:
                k = key(element)
                if k not in seen:
                    seen_add(k)
                    yield element


class ActivityCardMixin(object):
    select_related = ['organizer', 'sub_category__category', ]
    prefetch_related = ['pictures', 'calendars__sessions']


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
