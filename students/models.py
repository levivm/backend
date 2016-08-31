from django.core import signing
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from django.utils.translation import ugettext_lazy as _

import activities.constants as activities_constants
from activities.models import Activity
from locations.models import City
from utils.behaviors import Updateable

from utils.mixins import ImageOptimizable


class Student(ImageOptimizable, Updateable, models.Model):
    FEMALE, MALE = range(1, 3)

    GENDER_CHOICES = (
        (MALE, _('Hombre')),
        (FEMALE, _('Mujer'))
    )

    user = models.OneToOneField(User, related_name='student_profile')
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(null=True, blank=True, upload_to="avatars")
    birth_date = models.DateTimeField(null=True)
    city = models.ForeignKey(City, null=True)
    referrer_code = models.CharField(max_length=100, unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    verified_email = models.BooleanField(default=False)
    wish_list = models.ManyToManyField(Activity, through='WishList',
                                       related_name='wishlist_students')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.referrer_code = self.generate_referrer_code()

        if self.photo:
            self.photo.file.file = self.optimize(bytesio=self.photo.file.file,
                                                 width=self.photo.width, height=self.photo.height)

        super(Student, self).save(*args, **kwargs)

    @classmethod
    def get_by_email(cls, email):
        if not email:
            return None
        try:
            student = cls.objects.get(user__email=email)
            return student
        except Student.DoesNotExist:
            return None

    def update_base_info(self, data):
        self.user.__dict__.update(data)
        self.user.save()

    def generate_referrer_code(self):
        precode = '%(first_name)s%(last_name)s' % {
            'first_name': self.user.first_name.split(' ')[0].lower(),
            'last_name': self.user.last_name.split(' ')[0][0].lower()
            if self.user.last_name else '',
        }
        code_count = Student.objects.filter(referrer_code__startswith=precode).count() + 1
        return '%s%s' % (precode, code_count)

    def get_referral_url(self):
        return reverse('referrals:referrer', kwargs={'referrer_code': self.referrer_code})

    def get_referral_hash(self):
        return signing.dumps({'referrer_code': self.referrer_code})

    def get_photo_url(self):
        if self.photo:
            return self.photo.url

        return None

    def activities(self, status=None):
        # Proximas
        if status == activities_constants.NEXT:
            return [o.calendar.activity for o in
                    self.orders.select_related('calendar__activity').filter(
                        calendar__initial_date__gte=now())]
        # Iniciadas
        elif status == activities_constants.CURRENT:
            return [o.calendar.activity for o in
                    self.orders.select_related('calendar__activity').filter(
                        calendar__initial_date__lt=now())]
        # Por evaluar
        elif status == activities_constants.PAST:
            return [o.calendar.activity for o in
                    self.orders.select_related('calendar__activity').filter(
                        calendar__initial_date__lt=now() - timedelta(days=30)).order_by(
                        'calendar__initial_date')]
        else:
            return self.orders.select_related('calendar__activity').all()


class WishList(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
