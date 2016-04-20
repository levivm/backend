from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
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
    created_at = models.DateTimeField(auto_now_add=True)
    fee = models.ForeignKey(Fee, blank=True, null=True)
    is_free = models.BooleanField(default=False)

    objects = OrderQuerySet.as_manager()

    def change_status(self, status):
        self.status = status
        self.save(update_fields=['status'])

    @cached_property
    def total(self):
        _amount = self.get_total(self.student) - self.total_refunds_amount
        return _amount if _amount > 0 else 0

    @cached_property
    def total_net(self):
        if self.fee:
            return self.amount - (self.amount * self.fee.amount)
        return self.amount

    @cached_property
    def total_refunds_amount(self):
        # Substract approved refunds amounts
        amount = 0
        if self.refunds.exists():
            approved_refunds = self.refunds.filter(status=Refund.APPROVED_STATUS)

            refunds_total = sum(map(lambda x: x.amount, approved_refunds))
            amount += refunds_total

        return amount

    @cached_property
    def total_refunds_amount_without_coupon(self):
        # Substract approved refunds amounts
        amount = 0
        if self.refunds.exists():
            approved_refunds = self.refunds.filter(status=Refund.APPROVED_STATUS)

            refunds_total = sum(map(lambda x: x.amount_without_coupon, approved_refunds))
            amount += refunds_total

        return amount

    @cached_property
    def total_without_coupon(self):
        return self.amount - self.total_refunds_amount_without_coupon

    def get_total(self, student):
        if self.coupon and self.coupon.redeem_set.filter(student=student, used=True).exists():
            amount = self.amount - self.coupon.coupon_type.amount
            amount = 0 if amount < 0 else amount
        else:
            amount = self.amount

        return amount

    def get_organizer(self):
        return self.calendar.activity.organizer


class Assistant(Tokenizable):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    enrolled = models.BooleanField(default=True)

    objects = AssistantQuerySet.as_manager()

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def dismiss(self):
        self.enrolled = False
        self.save(update_fields=['enrolled'])

        if self.order.assistants.enrolled().count() == 0:
            self.order.change_status(Order.ORDER_CANCELLED_STATUS)


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

    def save(self, *args, **kwargs):
        if self.status == Refund.APPROVED_STATUS:
            if self.assistant is None:
                self.order.change_status(Order.ORDER_CANCELLED_STATUS)
            else:
                self.assistant.dismiss()

        super(Refund, self).save(*args, **kwargs)

    @cached_property
    def amount_without_coupon(self):
        amount = self.order.amount
        if self.assistant:
            amount /= self.order.quantity
        return amount

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
