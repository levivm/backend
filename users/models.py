from django.db import models
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.dispatch import receiver


_ = lambda x:x

#handler for signal after user singed up
@receiver(user_signed_up)
def after_sign_up(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']
    import pdb
    pdb.set_trace()
    profile = UserProfile.objects.create(user=user)
    user_type = request.POST.get('user_type',None) 
    if user_type:
        print "EL Usuario es",user_type
        print "EL Usuario es",user_type
        print "EL Usuario es",user_type
        #profile.user_type = request.POST.get('user_type')

    #profile.display_name = user.first_name + ' ' + user.last_name
    #profile.save()


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
