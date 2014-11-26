from django.db import models
from django.auth.models import User



# Create your models here.



class UserProfile(models.Model):

    FEMALE, MALE = range(2)


    GENDER_CHOICES = (
        (MALE, _('Hombre')),
        (FEMALE, _('Mujer'))
    )

    user   = models.OneToOneField(User, related_name='profile')
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, default=MALE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo     = models.CharField(max_length=100, verbose_name=_("Foto"), null=True, blank=True)
    birthday  = models.DateField()
    telephone = models.CharField(max_length=100)
    bio = models.TextField()







