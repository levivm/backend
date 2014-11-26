from django.db import models
from organizers.models import Organizer,Instructor

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length = 100)


class SubCategory(models.Model):
    name = models.CharField(max_length = 100)
    category = models.ForeignKey(Category)
    




class Activity(models.Model):

    LEVEL_CHOICES = (
        ('P','Principiante'),
        ('I','Intermedio'),
        ('A','Avanzado'),
        )

    DAY_CHOICES = (
        ('1','Lunes'),
        ('2','Martes'),
        ('3','Miercoles'),
        ('4','Jueves'),
        ('5','Viernes'),
        )

    TYPE_CHOICES = (
        ('C','Clase'),
        )


    type = models.CharField(max_length = 100,choices=TYPE_CHOICES,default='C')
    sub_category = models.ForeignKey(SubCategory) 
    organizer = models.ForeignKey(Organizer)
    #tags = models.ForeignKey()
    title = models.CharField(max_length = 100) 
    large_description = models.TextField()
    short_description = models.CharField(max_length = 100)
    level = models.CharField(choices = LEVEL_CHOICES, max_length = 1)
    goals = models.TextField(required=False)
    methodology = models.TextField()
    requirements = models.TextField()
    return_policy = models.TextField()
    #return_policy = models.ForeignKey(Return_Policies) *
    extra_info = models.TextField()
    #instructors = models.ForeignKey(Relación)
    #activities_-Contenido(Relación) -> Para después
    #sponsors = models.ForeignKey(Relación)
    #pictures = models.ForeignKey(Relación)
    youtube_video_url = models.CharField(max_length = 200)
    instructors = models.ManyToManyField(Instructor,related_name="activities")
    #attendant = models.ForeignKey(Relación) * 

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


class Categories(models.Model):
    name = models.CharField(max_length = 200)


class SubCategories(models.Model):
    name = models.CharField(max_length = 200)


















