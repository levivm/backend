from django.db import models
from reviews import constants as review_constants

class ReviewQuerySet(models.QuerySet):
    def by_status(self, status):
        if status == review_constants.READ:
            return self.filter(read=True)
        elif status == review_constants.UNREAD:
            return self.filter(read=False)
        else:
            return self
