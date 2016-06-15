from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from locations.models import City
from organizers.models import Organizer
from students.models import Student
from users.tasks import SendEmailOrganizerConfirmationTask


class RequestSignup(models.Model):
    DOCUMENT_TYPES = (
        ('cc', 'C.C.'),
        ('nit', 'N.I.T.'),
        ('ce', 'C.E.'),
    )

    email = models.EmailField(max_length=100)
    name = models.CharField(max_length=100)
    telephone = models.CharField(max_length=100)
    city = models.ForeignKey(City)
    document_type = models.CharField(choices=DOCUMENT_TYPES, max_length=5)
    document = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return "Nombre: %s - Email: %s - ID: %s" % (self.name, self.email, self.id)

    def save(self, *args, **kwargs):
        if self.approved and not hasattr(self, 'organizerconfirmation'):
            confirmation = OrganizerConfirmation.objects.create(requested_signup=self)
            confirmation.send()

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
        task = SendEmailOrganizerConfirmationTask()
        task.delay(self.id)


def get_profile(self):
    try:
        student = self.student_profile
    except Student.DoesNotExist:
        pass
    else:
        return student

    try:
        organizer = self.organizer_profile
    except Organizer.DoesNotExist:
        return None
    else:
        return organizer

User.add_to_class('get_profile', get_profile)
