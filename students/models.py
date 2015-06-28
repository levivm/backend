from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Student(models.Model):
    FEMALE, MALE = range(1,3)

    GENDER_CHOICES = (
        (MALE, _('Hombre')),
        (FEMALE, _('Mujer'))
    )

    user = models.OneToOneField(User, related_name='student_profile')
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, default=MALE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(null=True, blank=True, upload_to="avatars")
    birth_date = models.DateTimeField(null=True)



    @classmethod
    def get_by_email(cls,email):

    	try:
    		student = cls.objects.get(user__email=email)
    		return student
    	except Student.DoesNotExist:
    		return None

    def update(self,data):
        self.__dict__.update(data)
        self.save()

    def update_base_info(self,data):
        self.user.__dict__.update(data)
        self.user.save()



User.profile = property(lambda u: Student.objects.get_or_create(user=u)[0])
