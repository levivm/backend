from activities.tasks import ActivityScoreTask
from itertools import filterfalse


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
    select_related = ['location', 'organizer', 'sub_category', 'sub_category__category', 'organizer__user']
    prefetch_related = ['pictures', 'organizer__locations__city', 'organizer__instructors', 'calendars__sessions',
                        'calendars__orders__assistants', 'calendars__orders__student__user']
