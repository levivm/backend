import datetime
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
            filter(last_date__gte=today, *args, **kwargs)

    def closed(self, *args, **kwargs):
        today = datetime.datetime.today()
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(last_date__lt=today, *args, **kwargs)

    def unpublished(self, *args, **kwargs):
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(published=False, *args, **kwargs)