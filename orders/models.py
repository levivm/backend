from django.db import models
from activities.models import Chronogram
from students.models import Student


class Order(models.Model):
    chronogram = models.ForeignKey(Chronogram, related_name='orders')
    student = models.ForeignKey(Student)
    amount = models.FloatField()
    quantity = models.IntegerField()
    enroll = models.BooleanField(default=False)


class Assistant(models.Model):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
