# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

from organizers.models import Organizer, Instructor
from locations.models import Location
from utils.mixins import AssignPermissionsMixin
from django.utils.translation import ugettext_lazy as _



class Category(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category)


class Tags(models.Model):
    name = models.CharField(max_length=100, unique=True)
    occurrences = models.IntegerField(default=1)

    @classmethod
    def update_or_create(cls, tags_name):
        _tags = []
        for name in tags_name:
            tag, created = cls.objects.get_or_create(name=name)
            if not created:
                tag.occurrences += 1
                tag.save()

            _tags.append(tag)
        return _tags

    @classmethod
    def ready_to_use(cls):
        return cls.objects.filter(occurrences__gte=settings.TAGS_MIN_OCCOURRENCE)


class Activity(AssignPermissionsMixin, models.Model):
    LEVEL_CHOICES = (
        ('P',_('Principiante')),
        ('I',_('Intermedio')),
        ('A',_('Avanzado')),
        ('N',_('No Aplica'))
    )

    DAY_CHOICES = (
        ('1', _('Lunes')),
        ('2', _('Martes')),
        ('3', _('Miercoles')),
        ('4', _('Jueves')),
        ('5', _('Viernes')),
    )

    TYPE_CHOICES = (
        ('CU', u'Curso'),
        ('CE', u'Certificación'),
        ('CL', u'Clase'),
        ('DP', u'Diplomado'),
        ('SE', u'Seminario'),
        ('TA', u'Taller'),
    )
    permissions = ('organizers.delete_instructor', )

    sub_category = models.ForeignKey(SubCategory)
    organizer = models.ForeignKey(Organizer)
    tags = models.ManyToManyField(Tags)
    title = models.CharField(max_length=100)
    short_description = models.CharField(max_length=100)
    level = models.CharField(choices=LEVEL_CHOICES, max_length=1)
    goals = models.TextField(blank=True)
    methodology = models.TextField(blank=True)
    content = models.TextField(blank=True)
    audience = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    return_policy = models.TextField(blank=True)
    extra_info = models.TextField(blank=True)
    youtube_video_url = models.CharField(max_length=200, blank=True, null=True)
    instructors = models.ManyToManyField(Instructor, related_name="activities")
    enroll_open = models.NullBooleanField(default=True)
    published = models.NullBooleanField(default=False)
    certification = models.NullBooleanField(default=False)
    location = models.ForeignKey(Location, null=True)


    def update(self, data):
        self.__dict__.update(data)
        self.save()

    def steps_completed(self):


        steps_requirements = settings.REQUIRED_STEPS
        steps = steps_requirements.keys()
        # completed_steps = {}
        related_fields  = [rel.get_accessor_name() for rel in self._meta.get_all_related_objects()]
        related_fields += [rel.name for rel in self._meta.many_to_many]
        for step in steps:
            required_attrs = steps_requirements[step]
            for attr in required_attrs:

                if attr in related_fields:
                    if not getattr(self,attr,None).all():
                        return False
                        # break
                else:
                    if not  getattr(self,attr,None):
                        return False
                        # break
        return True


    @classmethod
    def get_types(cls):
        _types = cls.TYPE_CHOICES
        types = []
        for _type in _types:
            types.append({
                'code': _type[0],
                'value': _type[1],
            })
        return types

    @classmethod
    def get_levels(cls):
        _levels = cls.LEVEL_CHOICES
        levels = []
        for _level in _levels:
            levels.append({
                'code': _level[0],
                'value': _level[1],
            })
        return levels

    def publish(self):
        if self.steps_completed():
            self.published = True
            self.save(update_fields=['published'])
            return True
        return False

    def unpublish(self):
        self.published = False
        self.save(update_fields=['published'])
        

    def last_sale_date(self):

        chronograms = self.chronograms.values('sessions__date') \
            .order_by('-sessions__date').all()
        if not chronograms:
            return None

        return chronograms[0]['sessions__date']

    def add_instructors(self, instructors_data, organizer):
        instructors = Instructor.update_or_create(instructors_data, organizer)

        for instructor in instructors:
            self.assign_permissions(organizer.user, instructor)

        self.instructors.clear()
        self.instructors.add(*instructors)


class ActivityPhoto(models.Model):
    photo = models.ImageField(upload_to="activities")
    activity = models.ForeignKey(Activity, related_name="photos")
    main_photo = models.BooleanField(default=False)


class Chronogram(models.Model):
    activity = models.ForeignKey(Activity, related_name="chronograms")
    initial_date = models.DateTimeField()
    closing_sale = models.DateTimeField()
    number_of_sessions = models.IntegerField()
    session_price = models.FloatField()
    capacity = models.IntegerField()

    def update(self, data):
        self.__dict__.update(data)
        self.save()


class Session(models.Model):
    date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    chronogram = models.ForeignKey(Chronogram, related_name="sessions")


class Review(models.Model):
    description = models.CharField(max_length=200)
    activity = models.ForeignKey(Activity)
    author = models.CharField(max_length=200)
    rating = models.IntegerField()
    attributes = models.CharField(max_length=200)
