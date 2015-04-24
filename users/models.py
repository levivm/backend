from django.db import models
from django.contrib.auth.models import User, Group
from allauth.account.signals import user_signed_up,email_added
from django.dispatch import receiver
from .forms import UserCreateForm
from organizers.models import Organizer
from students.models import Student
from allauth.account.models import EmailAddress
from rest_framework.authtoken.models import Token

_ = lambda x:x

#handler for signal after user singed up
@receiver(user_signed_up)
def after_sign_up(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']    
    user_type = request.POST.get('user_type',None) 
    if user_type == 'S':
        Student.objects.create(user=user)
    elif user_type == 'O':
        Organizer.objects.create(user=user)
        organizers = Group.objects.get(name='Organizers')
        user.groups.add(organizers)

    Token.objects.create(user=user)


@receiver(email_added)
def after_email_added(sender, **kwargs):
    new_email = kwargs['email_address']
    user    = kwargs['user']  
    old_email = EmailAddress.objects.filter(user=user,primary=True).get()
    if old_email:
        new_email.set_as_primary()
        old_email.delete()


class UserProfile(models.Model):

    FEMALE, MALE = range(2)


    GENDER_CHOICES = (
        (MALE, _('Hombre')),
        (FEMALE, _('Mujer'))
    )

    user   = models.OneToOneField(User, related_name='profile')
    user_type = models.CharField(max_length=1,choices=UserCreateForm.USER_TYPES)
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, default=MALE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo      = models.CharField(max_length=100, verbose_name=_("Foto"), null=True, blank=True)
    birthday   = models.DateField(null=True,blank=True)
    telephone  = models.CharField(max_length=100,null=True,blank=True)
    bio = models.TextField(null=True,blank=True)