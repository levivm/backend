import string
import random
from django.db import models
from activities.models import Chronogram
from payments.models import Payment
from students.models import Student
from django.utils.translation import ugettext_lazy as _


TOKEN_SIZE = 5
def generate_token(size=TOKEN_SIZE):
    return ''.join(random.sample(string.ascii_uppercase, size))

ORDER_APPROVED_STATUS  = 'approved'
ORDER_PENDING_STATUS   = 'pending'
ORDER_CANCELLED_STATUS = 'cancelled'

class Order(models.Model):
    STATUS = (
        (ORDER_APPROVED_STATUS, _('Aprobada')),
        (ORDER_PENDING_STATUS, _('Pendiente')),
        (ORDER_CANCELLED_STATUS,_('Cancelada')),
    )
    chronogram = models.ForeignKey(Chronogram, related_name='orders')
    student = models.ForeignKey(Student, related_name='orders')
    amount = models.FloatField()
    quantity = models.IntegerField()
    status = models.CharField(choices=STATUS, max_length=15, default='pending')
    payment = models.OneToOneField(Payment)

    def change_status(self,status):
        self.status = status
        self.save()


class Assistant(models.Model):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    token = models.CharField(default=generate_token, max_length=TOKEN_SIZE)
