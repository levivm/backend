from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from activities.models import Calendar
from orders.querysets import OrderQuerySet, AssistantQuerySet
from payments.models import Payment
from students.models import Student
from utils.behaviors import Tokenizable


class Order(models.Model):
    ORDER_APPROVED_STATUS = 'approved'
    ORDER_PENDING_STATUS = 'pending'
    ORDER_CANCELLED_STATUS = 'cancelled'
    ORDER_DECLINED_STATUS = 'declined'

    STATUS = (
        (ORDER_APPROVED_STATUS, _('Aprobada')),
        (ORDER_PENDING_STATUS, _('Pendiente')),
        (ORDER_CANCELLED_STATUS, _('Cancelada')),
        (ORDER_DECLINED_STATUS, _('Declinada')),
    )
    calendar = models.ForeignKey(Calendar, related_name='orders')
    student = models.ForeignKey(Student, related_name='orders')
    amount = models.FloatField()
    quantity = models.IntegerField()
    status = models.CharField(choices=STATUS, max_length=15, default='pending')
    payment = models.OneToOneField(Payment, null=True)

    objects = OrderQuerySet.as_manager()

    def change_status(self, status):
        self.status = status
        self.save()


class Assistant(Tokenizable):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    enrolled = models.BooleanField(default=True)

    objects = AssistantQuerySet.as_manager()


class Refund(models.Model):
    STATUS = (
        ('approved', _('Approved')),
        ('pending', _('Pending')),
        ('declined', _('Declined')),
    )

    user = models.ForeignKey(User, related_name='refunds')
    order = models.ForeignKey(Order, related_name='refunds')
    assistant = models.ForeignKey(Assistant, blank=True, null=True, related_name='refunds')
    status = models.CharField(choices=STATUS, max_length=10, default='pending', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_at = models.DateTimeField(blank=True, null=True)
