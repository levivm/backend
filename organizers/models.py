from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from utils.models import CeleryTask


class Organizer(models.Model):
    user = models.OneToOneField(User, related_name='organizer_profile')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(null=True, blank=True, upload_to="avatars")
    telephone = models.CharField(max_length=100, blank=True)
    youtube_video_url = models.CharField(max_length=100, blank=True)
    website  = models.CharField(max_length=100, blank=True)
    headline = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    tasks = GenericRelation(CeleryTask)

    def __str__(self):
        return '%s' % (self.user.username)


# Create your models here.
class Instructor(models.Model):
    full_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    photo = models.CharField(max_length=1000, verbose_name=_("Foto"), null=True, blank=True)
    organizer = models.ForeignKey(Organizer, related_name="instructors", null=True)
    website = models.CharField(max_length=200, null=True, blank=True)


    @classmethod 
    def update_or_create(cls,instructors_data,organizer):

        instructors = []
        for ins in instructors_data:
            # Esto se usara en el futuro para asignar el instructor
            # al organizer
            # ins.update({'organizer':organizer})
            instructor = cls.objects.update_or_create(\
                    id=ins.get('id',None),\
                    defaults=ins)[0]        
            instructors.append(instructor)

        return instructors
