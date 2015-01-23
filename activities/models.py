# -*- coding: utf-8 -*-
from django.db import models
from organizers.models import Organizer,Instructor
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import F


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length = 100)
    category = models.ForeignKey(Category)

class Tags(models.Model):
    name  = models.CharField(max_length = 100,unique=True)
    occurrences = models.IntegerField(default=1) 


    @classmethod
    def update_or_create(cls,tags_name):
        _tags = []
        for name in tags_name:
            tag,created = cls.objects.get_or_create(name=name)
            if not created:
                tag.occurrences +=1
                tag.save()
            
            _tags.append(tag)
        return _tags



    @classmethod
    def ready_to_use(cls):
        return cls.objects.filter(occurrences__gte=settings.TAGS_MIN_OCCOURRENCE)

class Activity(models.Model):

    LEVEL_CHOICES = (
        ('P','Principiante'),
        ('I','Intermedio'),
        ('A','Avanzado'),
        ('N','No Aplica')
        )

    DAY_CHOICES = (
        ('1','Lunes'),
        ('2','Martes'),
        ('3','Miercoles'),
        ('4','Jueves'),
        ('5','Viernes'),
        )

    TYPE_CHOICES = (
        ('CU',u'Curso'),
        ('CE',u'Certificación'),
        ('CL',u'Clase'),
        ('DP',u'Diplomado'),
        ('SE',u'Seminario'),
        ('TA',u'Taller'),
        )




    # //     { label: 'Certificación', value: 1 },
    # //     { label: 'Curso', value: 2 },
    # //     { label: 'Clase', value: 3 },
    # //     { label: 'Diplomado', value: 4 },
    # //     { label: 'Seminario', value: 5 },
    # //     { label: 'Taller', value: 6 }



    type = models.CharField(max_length = 2,choices=TYPE_CHOICES)
    sub_category = models.ForeignKey(SubCategory) 
    organizer = models.ForeignKey(Organizer)
    tags = models.ManyToManyField(Tags,null=True)
    title = models.CharField(max_length = 100) 
    large_description = models.TextField()
    short_description = models.CharField(max_length = 100)
    level = models.CharField(choices = LEVEL_CHOICES, max_length = 1)
    goals = models.TextField()
    methodology = models.TextField()
    content = models.TextField()
    audience = models.TextField()
    requirements = models.TextField()
    return_policy = models.TextField()
    #return_policy = models.ForeignKey(Return_Policies) *
    extra_info = models.TextField()
    #instructors = models.ForeignKey(Relacion)
    #activities_-Contenido(Relacion) -> Para despues
    #sponsors = models.ForeignKey(Relacion)
    #pictures = models.ForeignKey(Relacion)
    youtube_video_url = models.CharField(max_length = 200)
    instructors = models.ManyToManyField(Instructor,related_name="activities")
    #attendant = models.ForeignKey(Relacion) * 
    active = models.NullBooleanField()

    @classmethod
    def get_types(cls):
        _types  = cls.TYPE_CHOICES
        types   = []
        for _type in _types:
            types.append({
                'code':_type[0],
                'value':_type[1],
                })
        return types

    @classmethod
    def get_levels(cls):
        _levels  = cls.LEVEL_CHOICES
        levels   = []
        for _level in _levels:
            levels.append({
                'code':_level[0],
                'value':_level[1],
                })
        return levels


class ActivityPhoto(models.Model):
    photo = models.CharField(max_length=1000, verbose_name=_("Foto"), null=True, blank=True)
    activity = models.ForeignKey(Activity)



class Chronogram(models.Model):
    activity = models.ForeignKey(Activity)
    initial_date = models.DateField()
    closing_sale = models.DateField()
    number_of_sessions = models.IntegerField()
    session_price = models.IntegerField()
    capacity = models.IntegerField()
    #location = models.CharField(max_length = 200)

    #chronogram_schedule = models.ForeignKey(Schedules)

class Schedule(models.Model):
    date = models.DateField()
    start_time = models.CharField(max_length = 100)
    end_time = models.CharField(max_length = 100)
    chronogram = models.ForeignKey(Chronogram)
    

class Review(models.Model):
    description = models.CharField(max_length = 200)
    activity    = models.ForeignKey(Activity)
    author      = models.CharField(max_length = 200)
    rating      = models.IntegerField()
    attributes  = models.CharField(max_length = 200)

# class ReturnPolicy(models.Model):
#     activity    = models.ForeignKey(Activity)
#     description = models.TextField()
#activity_name = models.ForeignKey(Activity)
#amount = models.IntegerField()
#transaction_number = models.IntegerField()
#date = models.DateField()



















# Create your models here.
