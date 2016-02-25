import datetime
import activities.constants as activities_constants
from django.db import models


class ActivityQuerySet(models.QuerySet):

    select_related_fields = ['organizer__user', 'sub_category__category', 'location__city']
    prefetch_related_fields = ['pictures', 'calendars__sessions',
                               'calendars__orders__refunds',
                               'calendars__orders__student__user',
                               'calendars__orders__assistants__refunds']

    def opened(self, *args, **kwargs):
        today = datetime.datetime.today()
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(last_date__gte=today, published=True, *args, **kwargs)

    def closed(self, *args, **kwargs):
        today = datetime.datetime.today()
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(last_date__lt=today, published=True, *args, **kwargs)

    def unpublished(self, *args, **kwargs):
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(published=False, *args, **kwargs)

    def by_student(self, student, status=None, *args, **kwargs):
        activities_q = self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(calendars__orders__student=student).distinct()

        today = datetime.datetime.today().date()
        if status == activities_constants.CURRENT:
            activities = activities_q.filter(calendars__initial_date__lte=today,
                                            last_date__gt=today)
        elif status == activities_constants.PAST:
            activities = activities_q.filter(last_date__lt=today)
        elif status == activities_constants.NEXT:
            activities = activities_q.filter(calendars__initial_date__gt=today)
        else:
            activities = activities_q.filter(calendars__initial_date__gt=today)

        return activities