# -*- coding: utf-8 -*-
import operator
from datetime import datetime
from functools import reduce
from django.utils.functional import cached_property
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.conf import settings
from random import randint
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from random import Random

from organizers.models import Organizer, Instructor
from locations.models import Location
from trulii.constants import MAX_ACTIVITY_INSTRUCTORS
from utils.mixins import AssignPermissionsMixin
from utils.behaviors import Updateable
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category)

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(max_length=100, unique=True)
    occurrences = models.IntegerField(default=1)

    def __str__(self):
        return self.name

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


class Activity(Updateable, AssignPermissionsMixin, models.Model):
    LEVEL_CHOICES = (
        ('P', _('Principiante')),
        ('I', _('Intermedio')),
        ('A', _('Avanzado')),
        ('N', _('No Aplica'))
    )

    DAY_CHOICES = (
        ('1', _('Lunes')),
        ('2', _('Martes')),
        ('3', _('Miercoles')),
        ('4', _('Jueves')),
        ('5', _('Viernes')),
    )

    permissions = ('organizers.delete_instructor',)

    sub_category = models.ForeignKey(SubCategory)
    organizer = models.ForeignKey(Organizer)
    tags = models.ManyToManyField(Tags)
    title = models.CharField(max_length=100)
    short_description = models.CharField(max_length=300)
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
    published = models.NullBooleanField(default=False)
    certification = models.NullBooleanField(default=False)
    location = models.ForeignKey(Location, null=True)
    tasks = GenericRelation('utils.CeleryTask')
    score = models.FloatField(default=0)

    def __str__(self):
        return self.title

    def steps_completed(self):
        steps_requirements = settings.REQUIRED_STEPS
        steps = steps_requirements.keys()
        related_fields = [rel.get_accessor_name() for rel in self._meta.get_all_related_objects()]
        related_fields += [rel.name for rel in self._meta.many_to_many]
        for step in steps:
            required_attrs = steps_requirements[step]
            for attr in required_attrs:

                if attr in related_fields:
                    if not getattr(self, attr, None).all():
                        return False
                        # break
                else:
                    if not getattr(self, attr, None):
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

    def update_tags(self,data):
        self.tags.clear()
        if data:
            tags = Tags.update_or_create(data)
            self.tags.clear()
            self.tags.add(*tags)


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

    def set_location(self, location):
        self.location = location
        self.save()

    def can_associate_instructor(self):
        if self.instructors.count() < MAX_ACTIVITY_INSTRUCTORS:
            return True

        return False

    def get_orders(self):
        chronograms = self.chronograms.all()
        orders = [c.orders.all() for c in chronograms]
        orders = [order for sublist in orders for order in sublist]
        return orders



class ActivityPhoto(models.Model):
    photo = models.ImageField(upload_to="activities")
    activity = models.ForeignKey(Activity, related_name="pictures")
    main_photo = models.BooleanField(default=False)

    @classmethod
    def create_from_stock(cls, stock_cover, activity):
        cls.objects.filter(activity=activity, main_photo=True).delete()
        return cls.objects.create(activity=activity, photo=stock_cover.photo, main_photo=True)


class ActivityStockPhoto(models.Model):
    photo = models.ImageField(upload_to="activities_stock")
    sub_category = models.ForeignKey(SubCategory)


    # @classmethod
    # def get_cover(cls,cover_id):
    #     try:
    #         cover = cls.objects.get(id=cover_id)
    #     except ActivityStockPhoto.DoesNotExist:


    @classmethod
    def get_random_pictures(cls,pictures_queryset,needed_pictures):
        count = pictures_queryset.count()
        top_count = needed_pictures
        if count < top_count:
            top_count = count

        random_indexes = Random().sample(range(0,count),top_count)  if count else []

        images = []

        for index in random_indexes:
            images.append(pictures_queryset[index])


        return images




    @classmethod
    def get_random_category_pictures(cls,sub_category,needed_pictures):
        pictures = cls.objects.filter(sub_category__category=sub_category.category)
        return cls.get_random_pictures(pictures,needed_pictures)






    @classmethod
    def get_images_by_subcategory(cls, sub_category):
        queryset = cls.objects.filter(sub_category=sub_category)
        sub_category_pictures = cls.get_random_pictures(queryset,\
                                    settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS)

        sub_category_pictures_amount = len(sub_category_pictures)
        enough_pictures = False if sub_category_pictures_amount < \
                                   settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS else True

        if not enough_pictures:
            needed_pictures_amount = abs(sub_category_pictures_amount - \
                                        settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS)

            category_pictures = cls.get_random_category_pictures(sub_category,\
                                        needed_pictures_amount)

            sub_category_pictures += category_pictures


        # category_images 
        return sub_category_pictures



class Chronogram(Updateable, models.Model):
    activity = models.ForeignKey(Activity, related_name="chronograms")
    initial_date = models.DateTimeField()
    closing_sale = models.DateTimeField()
    number_of_sessions = models.IntegerField()
    session_price = models.FloatField()
    capacity = models.IntegerField()
    enroll_open = models.NullBooleanField(default=True)
    is_weekend = models.NullBooleanField(default=False)
    is_free = models.BooleanField(default=False)
    tasks = GenericRelation('utils.CeleryTask')


    @cached_property
    def duration(self):
        """Returns calendar duration in ms"""
        sessions = self.sessions.all()
        get_datetime = lambda time:datetime.combine(datetime(1,1,1,0,0,0), time)
        timedeltas = map(lambda s:get_datetime(s.end_time)-get_datetime(s.start_time),sessions)
        duration = reduce(operator.add, timedeltas).total_seconds() 
        return duration 


    def available_capacity(self):
        #TODO cambiar filtro por constantes
        assistants = self.orders.filter(Q(status='approved') | \
                            Q(status='pending')).aggregate(num_assistants=Sum('quantity'))

        assistants = assistants['num_assistants'] or 0
        return self.capacity - assistants

    def get_assistants(self):
        return [a for o in self.orders.all() for a in o.assistants.all()]


class Session(models.Model):
    date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    chronogram = models.ForeignKey(Chronogram, related_name="sessions")
