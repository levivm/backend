from django.db import models
from django.contrib.auth.models import User

_ = lambda x: x


class Organizer(models.Model):

    user   = models.OneToOneField(User, related_name='organizer_profile')
    name   = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    photo      = models.ImageField(null=True, blank=True,upload_to="avatars")
    telephone  = models.CharField(max_length=100,blank=True)
    youtube_video_url = models.CharField(max_length=100,blank=True)
    website = models.CharField(max_length=100,blank=True)
    bio     = models.TextField(blank=True)

    

# Create your models here.
class Instructor(models.Model):
    full_name = models.CharField(max_length = 200)
    bio   = models.TextField(blank=True,null=True)
    photo = models.CharField(max_length=1000, verbose_name=_("Foto"), null=True, blank=True)
    organizer = models.ForeignKey(Organizer,related_name="instructors",null=True)
    website   = models.CharField(max_length=200,null=True,blank=True)



    @classmethod
    def update_or_create(cls,instructors_data,organizer):

        instructors = map(lambda ins:cls.objects.update_or_create(\
                                        organizer=organizer,id=ins.get('id',None),\
                                        defaults=ins)[0],\
                          instructors_data)

        return list(instructors)
        

