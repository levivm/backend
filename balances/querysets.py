from django.db import models


class BalanceLogQuerySet(models.QuerySet):
    def available(self, *args, **kwargs):
        return self.filter(status='available', *args, **kwargs)

    def unavailable(self, *args, **kwargs):
        return self.filter(status='unavailable', *args, **kwargs)
