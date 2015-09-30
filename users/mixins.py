from students.models import Student
from organizers.models import Organizer
from django.http import Http404




class UserTypeMixin(object):


    def get_student(self,user,exception=Http404):
        try:
            return user.student_profile
        except Student.DoesNotExist:
            raise exception

    def get_organizer(self,user,exception=Http404):
        try:
            return user.organizer_profile
        except Organizer.DoesNotExist:
            raise exception

