from django.db import models
from django.db.models.query_utils import Q


class OrderQuerySet(models.QuerySet):
    def available(self, *args, **kwargs):
        return self.filter(Q(status='approved') | Q(status='pending'), *args, **kwargs)

    def unavailable(self, *args, **kwargs):
        return self.filter(Q(status='declined') | Q(status='cancelled'), *args, **kwargs)


class AssistantQuerySet(models.QuerySet):
    def enrolled(self, *args, **kwargs):
        return self.filter(enrolled=True, *args, **kwargs)

    def dismissed(self, *args, **kwargs):
        return self.filter(enrolled=False, *args, **kwargs)
