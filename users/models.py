from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up,email_added
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation
from django.dispatch import receiver
from organizers.models import Organizer
from students.models import Student
from rest_framework.authtoken.models import Token
from locations.models import City
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import datetime


_ = lambda x:x

#handler for signal after user singed up
@receiver(user_signed_up)
def after_sign_up(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']    
    data = request.POST
    user_type = data.get('user_type') 
    if user_type == 'S':
        profile = Student.objects.create(user=user)
        profile.save()
        send_email_confirmation(request,user,signup=True)
    elif user_type == 'O':
        
        # try:
        #     OrganizerConfirmation.objects.\
        #         select_related('requested_signup').\
        #         get(requested_signup__email=user.email)
        name = data.get('name')
        profile = Organizer.objects.create(user=user,name=name)
        profile.save()



    # get_adapter().login(request,user)


        # except OrganizerConfirmation.DoesNotExist:
        #     print "USERRRRR ID ",user.id
        #     a = EmailAddress.objects.filter(user=user,primary=True).get()
        #     print a.id
        #     user.delete()
            # return

    
    # Token.objects.create(user=user)



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

    USER_TYPES = (
        ('O', _('Organizador')),
        ('S', _('Estudiante')),
    )


    user   = models.OneToOneField(User, related_name='profile')
    user_type = models.CharField(max_length=1,choices=USER_TYPES)
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, default=MALE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo      = models.CharField(max_length=100, verbose_name=_("Foto"), null=True, blank=True)
    birthday   = models.DateField(null=True,blank=True)
    telephone  = models.CharField(max_length=100,null=True,blank=True)
    bio = models.TextField(null=True,blank=True)






class RequestSignup(models.Model):
    email = models.EmailField(max_length=100)
    name  = models.CharField(max_length=100)
    telephone =  models.CharField(max_length=100)
    want_to_teach = models.TextField()
    city = models.ForeignKey(City)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return "Nombre: %s - Email: %s - ID: %s" % (self.name,self.email,self.id)

    def save(self, *args, **kwargs):

        print "saving",self.approved
        if  self.approved:
            instance,created = OrganizerConfirmation.objects.get_or_create(requested_signup=self)
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
                (self.requested_signup.id,self.id)


    def save(self, *args, **kwargs):

        if not self.pk:
            self.key = self.generate_key()

        super(OrganizerConfirmation, self).save(*args, **kwargs)


    def generate_key(self):
        return get_random_string(64).lower()


    def get_confirmation_url(self):
        base_url = settings.FRONT_SERVER_URL
        rest_url = "organizers/register/%s/"%(self.key)
        return base_url + rest_url


    def send(self):

        ctx = {
            'activate_url' : self.get_confirmation_url(),
            'organizer' : self.requested_signup.name

        }
        email_template = "account/email/request_signup_confirmation"
        get_adapter().send_mail(email_template,
                                self.requested_signup.email,
                                ctx)
        self.sent = datetime.now()
        self.save()


