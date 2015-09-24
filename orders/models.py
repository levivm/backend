from django.db import models
from django.utils.translation import ugettext_lazy as _

from activities.models import Chronogram
from payments.models import Payment
from students.models import Student
from utils.behaviors import Tokenizable


class Order(models.Model):

    ORDER_APPROVED_STATUS  = 'approved'
    ORDER_PENDING_STATUS   = 'pending'
    ORDER_CANCELLED_STATUS = 'cancelled'
    ORDER_DECLINED_STATUS  = 'declined'


    STATUS = (
        (ORDER_APPROVED_STATUS, _('Aprobada')),
        (ORDER_PENDING_STATUS, _('Pendiente')),
        (ORDER_CANCELLED_STATUS,_('Cancelada')),
        (ORDER_DECLINED_STATUS,_('Declinada')),
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


class Assistant(Tokenizable):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
