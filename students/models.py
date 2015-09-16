from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from locations.models import City
from django.contrib.contenttypes.fields import GenericRelation
from utils.models import CeleryTask


class Student(models.Model):
    FEMALE, MALE = range(1, 3)

    GENDER_CHOICES = (
        (MALE, _('Hombre')),
        (FEMALE, _('Mujer'))
    )

    user = models.OneToOneField(User, related_name='student_profile')
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, default=MALE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(null=True, blank=True, upload_to="avatars")
    birth_date = models.DateTimeField(null=True)
    city = models.ForeignKey(City, null=True)
    tasks = GenericRelation(CeleryTask)
    referrer_code = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.referrer_code = self.generate_referrer_code()
        super(Student, self).save(*args, **kwargs)

    @classmethod
    def get_by_email(cls, email):

        try:
            student = cls.objects.get(user__email=email)
            return student
        except Student.DoesNotExist:
            return None

    def update(self, data):
        self.__dict__.update(data)
        city = data.get('city')

        if city:
            self.city = city

        self.save()

    def updated_city(self, city):
        self.city = city
        self.save()

    def update_base_info(self, data):
        self.user.__dict__.update(data)
        self.user.save()

    def generate_referrer_code(self):
        precode = '%(first_name)s%(last_name)s' % {
            'first_name': self.user.first_name.split(' ')[0].lower(),
            'last_name': self.user.last_name.split(' ')[0][0].lower(),
        }
        code_count = Student.objects.filter(referrer_code__startswith=precode).count() + 1
        return '%s%s' % (precode, code_count)


User.profile = property(lambda u: Student.objects.get_or_create(user=u)[0])
