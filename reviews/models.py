from django.db import models
from activities.models import Activity
from students.models import Student


class Review(models.Model):
    rating = models.FloatField()
    comment = models.CharField(blank=True, max_length=480)
    reply = models.CharField(blank=True, max_length=480)
    activity = models.ForeignKey(Activity, related_name='reviews')
    author = models.ForeignKey(Student, related_name='reviews')

    class Meta:
        permissions = (
            ('report_review', 'Report review'),
            ('reply_review', 'Reply review'),
        )
