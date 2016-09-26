from django.db import models


class OrganizerQuerySet(models.QuerySet):

    def featured(self, *args, **kwargs):
        return self.filter(feature=True, *args, **kwargs)

    def special(self, *args, **kwargs):
        return self.filter(type='special', *args, **kwargs)
