import statistics

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.dispatch import receiver

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
    replied_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        permissions = (
            ('report_review', 'Report review'),
            ('reply_review', 'Reply review'),
            ('read_review', 'Read review'),
        )


# Signals

def update_organizer_rating(organizer):
    ratings = [a.rating for a in organizer.activity_set.all()]
    average = statistics.mean(ratings) if ratings else 0
    organizer.rating = average
    organizer.save(update_fields=['rating'])

def update_activity_rating(activity):
    ratings = [r.rating for r in activity.reviews.all()]
    average = statistics.mean(ratings) if ratings else 0
    activity.rating = average
    activity.save(update_fields=['rating'])

@receiver(models.signals.post_save, sender=Review, dispatch_uid='post_save_rating_update')
def post_save_rating_update(sender, instance, created, **kwargs):
    if created:
        update_activity_rating(instance.activity)
        update_organizer_rating(instance.activity.organizer)

@receiver(models.signals.post_delete, sender=Review, dispatch_uid='post_delete_rating_update')
def post_delete_rating_update(sender, instance, **kwargs):
    update_activity_rating(instance.activity)
    update_organizer_rating(instance.activity.organizer)
