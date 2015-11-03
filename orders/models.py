from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from activities.models import Calendar
from orders.querysets import OrderQuerySet, AssistantQuerySet
from payments.models import Payment, Fee
from referrals.models import Coupon, Redeem
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
    coupon = models.ForeignKey(Coupon, null=True)
    fee = models.ForeignKey(Fee, blank=True, null=True)

    objects = OrderQuerySet.as_manager()

    def change_status(self, status):
        self.status = status
        self.save(update_fields=['status'])

    def get_total(self, student):
        if self.coupon and self.coupon.redeem_set.filter(student=student, used=True).exists():
            amount = self.amount - self.coupon.coupon_type.amount
            amount = 0 if amount < 0 else amount
        else:
            amount = self.amount

        return amount


class Assistant(Tokenizable):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    enrolled = models.BooleanField(default=True)

    objects = AssistantQuerySet.as_manager()

    def dismiss(self):
        self.enrolled = False
        self.save(update_fields=['enrolled'])


class Refund(models.Model):
    APPROVED_STATUS = 'approved'
    PENDING_STATUS = 'pending'
    DECLINED_STATUS = 'declined'

    STATUS = (
        (APPROVED_STATUS, _('Aprobado')),
        (PENDING_STATUS, _('Pendiente')),
        (DECLINED_STATUS, _('Rechazado')),
    )

    user = models.ForeignKey(User, related_name='refunds')
    order = models.ForeignKey(Order, related_name='refunds')
    assistant = models.ForeignKey(Assistant, blank=True, null=True, related_name='refunds')
    status = models.CharField(choices=STATUS, max_length=10, default=PENDING_STATUS, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('order', 'assistant')

    def __str__(self):
        return '%s: %s' % (self.user.username, self.order.id)

    @cached_property
    def amount(self):
        profile = self.user.get_profile()
        if isinstance(profile, Student):
            amount = self.order.get_total(profile)
        else:
            amount = self.order.amount

        if self.assistant:
            amount /= self.order.quantity

        return amount
