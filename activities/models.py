# -*- coding: utf-8 -*-
import io
import os
from datetime import datetime, date
from random import Random

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField

from locations.models import Location
from organizers.models import Organizer, Instructor
from utils.behaviors import Updateable
from utils.mixins import AssignPermissionsMixin, ImageOptimizable
from utils.models import CeleryTaskEditActivity
from . import constants as activities_constants
from .queryset import ActivityQuerySet


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20)
    slug = models.SlugField(blank=True)
    headline = models.TextField(blank=True)
    description = models.TextField(blank=True)
    cover_photo = models.ImageField(upload_to='categories/', blank=True)
    content_photo = models.ImageField(upload_to='categories/', blank=True)
    seo_data = JSONField(default={})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(Category, self).save(*args, **kwargs)


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category)
    featured = models.BooleanField(default=False)

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
        return cls.objects.filter(occurrences__gte=activities_constants.TAGS_MIN_OCCOURRENCE)


class Activity(Updateable, AssignPermissionsMixin, models.Model):
    LEVEL_CHOICES = (
        (activities_constants.LEVEL_P, _('Principiante')),
        (activities_constants.LEVEL_I, _('Intermedio')),
        (activities_constants.LEVEL_A, _('Avanzado')),
        (activities_constants.LEVEL_N, _('No Aplica'))
    )

    DAY_CHOICES = (
        ('1', _('Lunes')),
        ('2', _('Martes')),
        ('3', _('Miercoles')),
        ('4', _('Jueves')),
        ('5', _('Viernes')),
    )

    permissions = ('activities.change_activity', 'organizers.delete_activity')

    sub_category = models.ForeignKey(SubCategory, on_delete=models.DO_NOTHING)
    organizer = models.ForeignKey(Organizer)
    tags = models.ManyToManyField(Tags)
    title = models.CharField(max_length=100)
    short_description = models.TextField()
    level = models.CharField(choices=LEVEL_CHOICES, max_length=1)
    goals = models.TextField(blank=True)
    methodology = models.TextField(blank=True)
    content = models.TextField(blank=True)
    audience = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    post_enroll_message = models.TextField(blank=True)
    return_policy = models.TextField(blank=True)
    extra_info = models.TextField(blank=True)
    youtube_video_url = models.CharField(max_length=200, blank=True, null=True)
    instructors = models.ManyToManyField(Instructor, related_name="activities", blank=True)
    published = models.NullBooleanField(default=False)
    certification = models.NullBooleanField(default=False)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    score = models.FloatField(default=0)
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    objects = ActivityQuerySet.as_manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Activity, self).save(user=self.organizer.user, obj=self, *args, **kwargs)

    def steps_completed(self):
        steps_requirements = activities_constants.REQUIRED_STEPS
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

    @cached_property
    def wishlist_count(self):
        return self.wishlist_students.count()

    def update_tags(self, data):
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

    def closest_calendar(self, initial_date=None, cost_start=None, cost_end=None, is_free=None):
        today = date.today()
        closest = None
        query = Q()
        if is_free:
            query &= Q(is_free=True)

        elif cost_start is not None and cost_end is not None:
            without_limit = True if int(cost_end) == settings.PRICE_RANGE.get('max') else False
            if without_limit:
                query &= Q(session_price__gte=(cost_start)) |\
                    Q(packages__price__gte=(cost_start))
            else:
                query &= Q(session_price__range=(cost_start, cost_end)) |\
                    Q(packages__price__range=(cost_start, cost_end))

        if initial_date is not None:
            initial_date = datetime.fromtimestamp(int(initial_date) // 1000).date()
            query = query & Q(initial_date__gte=initial_date)

        query = query & Q(available_capacity__gt=0, enroll_open=True)

        calendars = self.calendars.filter(query)

        if calendars:
            if is_free:
                open_calendars = [c for c in calendars if c.initial_date >= today and c.is_free]
            else:
                open_calendars = [c for c in calendars if c.initial_date >= today]

            if open_calendars:
                closest = sorted(open_calendars, key=lambda c: c.initial_date)[0]
            else:

                if is_free:
                    calendars = [c for c in calendars if c.initial_date < today and c.is_free]
                else:
                    calendars = [c for c in calendars if c.initial_date < today]

                if calendars:
                    closest = sorted(calendars, key=lambda c: c.initial_date, reverse=True)[0]

        return closest

    def set_location(self, location):
        self.location = location
        self.save()

    def can_associate_instructor(self):
        if self.instructors.count() < activities_constants.MAX_ACTIVITY_INSTRUCTORS:
            return True

        return False

    def get_orders(self):
        calendars = self.calendars.all()
        orders = [c.orders.all() for c in calendars]
        orders = [order for sublist in orders for order in sublist]
        return orders

    def get_assistants(self):
        return [assistant for order in self.get_orders() for assistant in
                      order.assistants.all()]

    def get_frontend_url(self):
        return '%sactivity/%s' % (settings.FRONT_SERVER_URL, self.id)


class ActivityPhoto(AssignPermissionsMixin, ImageOptimizable, models.Model):
    photo = models.ImageField(upload_to="activities")
    thumbnail = models.ImageField(upload_to='activities', blank=True, null=True)
    activity = models.ForeignKey(Activity, related_name="pictures")
    main_photo = models.BooleanField(default=False)

    permissions = ('activities.delete_activityphoto',)

    def save(self, *args, **kwargs):
        if not self.thumbnail:
            filename = os.path.split(self.photo.name)[-1]
            simple_file = self.create_thumbnail(bytesio=io.BytesIO(self.photo.read()),
                                                filename=filename,
                                                width=400, height=350)
            self.thumbnail.save(
                'thumbnail_%s' % filename,
                simple_file,
                save=False)

        super(ActivityPhoto, self). \
            save(user=self.activity.organizer.user, obj=self, *args, **kwargs)

    @classmethod
    def create_from_stock(cls, stock_cover, activity):
        cls.objects.filter(activity=activity, main_photo=True).delete()
        return cls.objects.create(activity=activity, photo=stock_cover.photo, main_photo=True)


class ActivityStockPhoto(models.Model):
    photo = models.ImageField(upload_to="activities_stock")
    sub_category = models.ForeignKey(SubCategory)

    @classmethod
    def get_random_pictures(cls, pictures_queryset, needed_pictures):
        count = pictures_queryset.count()
        top_count = needed_pictures
        if count < top_count:
            top_count = count

        random_indexes = Random().sample(range(0, count), top_count) if count else []

        images = []

        for index in random_indexes:
            images.append(pictures_queryset[index])

        return images

    @classmethod
    def get_random_category_pictures(cls, sub_category, needed_pictures):
        pictures = cls.objects.filter(sub_category__category=sub_category.category)
        return cls.get_random_pictures(pictures, needed_pictures)

    @classmethod
    def get_images_by_subcategory(cls, sub_category):
        queryset = cls.objects.filter(sub_category=sub_category)
        sub_category_pictures = cls.get_random_pictures(queryset,
                                                        activities_constants.
                                                        MAX_ACTIVITY_POOL_STOCK_PHOTOS)

        sub_category_pictures_amount = len(sub_category_pictures)
        enough_pictures = False if sub_category_pictures_amount < \
            activities_constants.MAX_ACTIVITY_POOL_STOCK_PHOTOS \
            else True

        if not enough_pictures:
            needed_pictures_amount = abs(sub_category_pictures_amount -
                                         activities_constants.MAX_ACTIVITY_POOL_STOCK_PHOTOS)

            category_pictures = cls.get_random_category_pictures(sub_category,
                                                                 needed_pictures_amount)

            sub_category_pictures += category_pictures

        # category_images
        return sub_category_pictures


class Calendar(Updateable, AssignPermissionsMixin, models.Model):
    activity = models.ForeignKey(Activity, related_name="calendars")
    initial_date = models.DateField()
    session_price = models.FloatField(blank=True, null=True)
    enroll_open = models.BooleanField(default=True)
    is_weekend = models.NullBooleanField(default=False)
    is_free = models.BooleanField(default=False)
    available_capacity = models.IntegerField()
    note = models.CharField(max_length=200, blank=True)
    schedules = models.TextField()

    permissions = ('activities.change_calendar', 'activities.delete_calendar')

    def __str__(self):
        return '%s - id: %s' % (self.initial_date.strftime('%d de %B de %Y'), self.id)

    def save(self, *args, **kwargs):
        super(Calendar, self).save(user=self.activity.organizer.user, obj=self, *args, **kwargs)

    @cached_property
    def num_enrolled(self):
        return sum([o.num_enrolled() for o in self.orders.available()])

    def get_assistants(self):
        orders_qs = self.orders.all()
        return [a for o in orders_qs if o.status == 'approved' or o.status == 'pending' for a in
                o.assistants.all() if a.enrolled]

    def increase_capacity(self, amount):
        # Dont increase capacity over open activities
        if self.activity.is_open:
            return

        self.available_capacity = self.available_capacity + amount
        self.save(update_fields=['available_capacity'])

    def decrease_capacity(self, amount):
        # Dont decrease capacity over open activities
        if self.activity.is_open:
            return

        self.available_capacity = self.available_capacity - amount
        self.save(update_fields=['available_capacity'])

    # TODO hacer test de esto
    def filter_packages_by_price(self, cost_start=None, cost_end=None):
        query = Q()
        if cost_start is not None and cost_end is not None:
            without_limit = True if int(cost_end) == settings.PRICE_RANGE.get('max') else False
            if without_limit:
                query &= Q(price__gte=cost_start)
            else:
                query &= Q(price__range=(cost_start, cost_end))

        return self.packages.filter(query) if query else self.packages.all()


class CalendarPackage(Updateable, models.Model):

    MONTH, CLASS = range(1, 3)
    TYPE_CHOICES = (
        (MONTH, 'Mes(es)'),
        (CLASS, 'Clase(s)'),
    )

    type = models.PositiveIntegerField(choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    calendar = models.ForeignKey(Calendar, related_name='packages')

    class Meta:
        ordering = ['price']


class ActivityCeleryTaskEditActivity(CeleryTaskEditActivity):
    activity = models.ForeignKey('Activity', related_name='tasks')


class CalendarCeleryTaskEditActivity(CeleryTaskEditActivity):
    calendar = models.ForeignKey('Calendar', related_name='tasks')


class ActivityStats(models.Model):
    activity = models.OneToOneField(Activity, related_name='stats')
    views_counter = models.PositiveIntegerField(default=0)


# Signals

from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=SubCategory)
def move_activities_to_other(sender, instance, **kwargs):
    other = SubCategory.objects.get(name='Otros', category=instance.category)
    instance.activity_set.all().update(sub_category=other)

@receiver(pre_delete, sender=Category)
def move_activities_to_category_other(sender, instance, **kwargs):
    other = SubCategory.objects.get(name='Otros', category__name='Otros')
    Activity.objects.filter(sub_category__category=instance) \
        .update(sub_category=other)
