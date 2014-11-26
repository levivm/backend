from django.db import models
from activities.models import Activity
from django.auth.models import User





class Organizer(models.Model):

    user   = models.OneToOneField(User, related_name='profile')
	name   = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    photo      = models.CharField(max_length=100, verbose_name=_("Foto"), null=True, blank=True)
    telephone  = models.CharField(max_length=100)
    youtube_video_url = models.CharField(max_length=100)
    website = models.CharField(max_length=100)
    bio     = models.TextField()

    

# Create your models here.
class Instructor(models.Model):
    full_name = models.CharField(max_length = 200)
    bio   = models.TextField()
    photo = models.CharField(max_length=1000, verbose_name=_("Foto"), null=True, blank=True)
    organizer = models.ForeignKey(Organizer,related_name="instructors")