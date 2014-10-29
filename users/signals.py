from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from students.models import Student



#handler for signal after user singed up
@receiver(user_signed_up)
def after_sign_up(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']
    #check the user type and create the corresponding model
    
    #profile = UserProfile.objects.create(user=user)
    # if request.POST.get('user_type'):
    #     profile.user_type = request.POST.get('user_type')

    # profile.display_name = user.first_name + ' ' + user.last_name
    # profile.save()
