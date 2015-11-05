from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from activities.models import Activity
from students.models import Student


class Review(models.Model):
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    comment = models.CharField(blank=True, max_length=480)
    reply = models.CharField(blank=True, max_length=480)
    activity = models.ForeignKey(Activity, related_name='reviews')
    author = models.ForeignKey(Student, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)
    reported = models.BooleanField(default=False)
    read = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ('report_review', 'Report review'),
            ('reply_review', 'Reply review'),
        )
