from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from allauth.account.signals import user_signed_up, email_added
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from django.utils import timezone
from django.utils.crypto import get_random_string

from organizers.models import Organizer
from students.models import Student
from locations.models import City


_ = lambda x: x

# handler for signal after user singed up
@receiver(user_signed_up)
def after_sign_up(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']
    data = request.POST
    user_type = data.get('user_type')
    group = None
    if user_type == 'S':
        student = Student.objects.create(user=user)
        assign_perm('students.change_student', user, student)
        group = Group.objects.get(name='Students')
        if not user.socialaccount_set.exists():
            send_email_confirmation(request, user, signup=True)
    elif user_type == 'O':
        name = data.get('name')
        organizer = Organizer.objects.create(user=user, name=name)
        assign_perm('organizers.change_organizer', user, organizer)
        group = Group.objects.get(name='Organizers')

    user.groups.add(group)


@receiver(email_added)
def after_email_added(sender, **kwargs):
    new_email = kwargs['email_address']
    user = kwargs['user']
    old_email = EmailAddress.objects.filter(user=user, primary=True).get()
    if old_email:
        new_email.set_as_primary()
        old_email.delete()


class UserProfile(models.Model):
    FEMALE, MALE = range(2)

    GENDER_CHOICES = (
        (MALE, _('Hombre')),
        (FEMALE, _('Mujer'))
    )

    USER_TYPES = (
        ('O', _('Organizador')),
        ('S', _('Estudiante')),
    )

    user = models.OneToOneField(User, related_name='profile')
    user_type = models.CharField(max_length=1, choices=USER_TYPES)
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, default=MALE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.CharField(max_length=100, verbose_name=_("Foto"), null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)


class RequestSignup(models.Model):
    email = models.EmailField(max_length=100)
    name = models.CharField(max_length=100)
    telephone = models.CharField(max_length=100)
    want_to_teach = models.TextField()
    city = models.ForeignKey(City)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return "Nombre: %s - Email: %s - ID: %s" % (self.name, self.email, self.id)

    def save(self, *args, **kwargs):
        if self.approved:
            instance, created = OrganizerConfirmation.objects.get_or_create(requested_signup=self)
            if created:
                instance.save()

            instance.send()

        super(RequestSignup, self).save(*args, **kwargs)


class OrganizerConfirmation(models.Model):
    requested_signup = models.OneToOneField(RequestSignup)
    created = models.DateTimeField(verbose_name=_('created'),
                                   default=timezone.now)
    key = models.CharField(verbose_name=_('key'), max_length=64, unique=True)
    sent = models.DateTimeField(verbose_name=_('sent'), null=True)
    used = models.BooleanField(default=False)

    def __unicode__(self):
        return "Requested Signup ID: %s - ID: %s" % \
               (self.requested_signup.id, self.id)


    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = self.generate_key()

        super(OrganizerConfirmation, self).save(*args, **kwargs)


    def generate_key(self):
        return get_random_string(64).lower()


    def get_confirmation_url(self):
        base_url = settings.FRONT_SERVER_URL
        rest_url = "organizers/register/%s/" % (self.key)
        return base_url + rest_url


    def send(self):
        ctx = {
            'activate_url': self.get_confirmation_url(),
            'organizer': self.requested_signup.name

        }
        email_template = "account/email/request_signup_confirmation"
        get_adapter().send_mail(email_template,
                                self.requested_signup.email,
                                ctx)
        self.sent = datetime.now()
        self.save()
