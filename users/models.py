from django.db import models
from django.auth.models import User

# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(User, related_name='profile')
