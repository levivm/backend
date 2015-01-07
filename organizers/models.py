from django.db import models
from django.contrib.auth.models import User

_ = lambda x: x


class Organizer(models.Model):

    user   = models.OneToOneField(User, related_name='organizer_profile')
    name   = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    photo      = models.ImageField(null=True, blank=True,upload_to="avatars")
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