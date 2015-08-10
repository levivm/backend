import string
import random
from django.db import models
from activities.models import Chronogram
from payments.models import Payment
from students.models import Student

TOKEN_SIZE = 5
def generate_token(size=TOKEN_SIZE):
    return ''.join(random.sample(string.ascii_uppercase, size))

class Order(models.Model):
    STATUS = (
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    )
    chronogram = models.ForeignKey(Chronogram, related_name='orders')
    student = models.ForeignKey(Student, related_name='orders')
    amount = models.FloatField()
    quantity = models.IntegerField()
    status = models.CharField(choices=STATUS, max_length=15, default='pending')
    payment = models.OneToOneField(Payment)


class Assistant(models.Model):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    token = models.CharField(default=generate_token, max_length=TOKEN_SIZE)
