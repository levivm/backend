from django.db import models
from django.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Create your models here.


# Create your models here.

class Student(models.Model):

    FEMALE, MALE = range(2)


    GENDER_CHOICES = (
        (MALE, _('Hombre')),
        (FEMALE, _('Mujer'))
    )

    user = models.OneToOneField(User, related_name='profile')
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, default=MALE)
    created_at = models.DateTimeField(auto_now_add=True)




User.profile = property(lambda u: Student.objects.get_or_create(user=u)[0])
