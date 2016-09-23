import numbers
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField

from activities.models import Calendar
from organizers.models import OrganizerBankInfo
from orders.querysets import OrderQuerySet, AssistantQuerySet
from payments.models import Payment, Fee
from referrals.models import Coupon
from students.models import Student
from utils.behaviors import Tokenizable


class Order(models.Model):
    ORDER_APPROVED_STATUS = 'approved'
    ORDER_PENDING_STATUS = 'pending'
    ORDER_CANCELLED_STATUS = 'cancelled'
    ORDER_DECLINED_STATUS = 'declined'
    ORDER_STATUS_FIELD = 'status'

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
    package_quantity = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(choices=STATUS, max_length=15, default='pending')
    payment = models.OneToOneField(Payment, null=True)
    coupon = models.ForeignKey(Coupon, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    fee = models.FloatField(default=0)
    is_free = models.BooleanField(default=False)
    fee_detail = JSONField(default={})

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            new_status = self.status
            original_order = Order.objects.get(pk=self.pk)
            original_status = original_order.status

            if not original_status == new_status:
                if new_status in [self.ORDER_APPROVED_STATUS, self.ORDER_PENDING_STATUS]:
                    self.calendar.decrease_capacity(self.num_enrolled())
                elif new_status in [self.ORDER_CANCELLED_STATUS, self.ORDER_DECLINED_STATUS]:
                    self.calendar.increase_capacity(self.num_enrolled())

        super(Order, self).save(*args, **kwargs)

    @classmethod
    def get_fee_detail(cls, order, is_free, payment, organizer_regimen):

        fee_detail = cls.get_total_fee(payment.payment_type,
                                       order.amount, organizer_regimen)\
            if not is_free else cls.get_total_free_fee(order)

        return fee_detail

    def num_enrolled(self):
        return self.assistants.enrolled().count()

    def change_status(self, status):

        self.status = status
        self.save(update_fields=['status'])

    @cached_property
    def total(self):
        _amount = self.get_total(self.student)
        return _amount if _amount > 0 else 0

    @cached_property
    def total_net(self):
        if self.fee:
            return self.amount - self.fee
        return self.amount

    @cached_property
    def total_without_coupon(self):
        return self.amount

    def get_total(self, student):
        if self.coupon and self.coupon.redeem_set.filter(student=student, used=True).exists():
            amount = self.amount - self.coupon.coupon_type.amount
            amount = 0 if amount < 0 else amount
        else:
            amount = self.amount

        return amount

    def get_organizer(self):
        return self.calendar.activity.organizer

    @classmethod
    def get_total_free_fee(cls, order):
        return {
            'final_total': order.amount,
            'total_fee': 0,
        }

    @classmethod
    def get_total_fee(cls, payment_type, base, regimen):

        fees = Fee.get_fees_dict()

        IVA = fees.get('iva')

        renta = 0
        ica = 0
        reteiva = 0
        reteica = 0

        # Trulii fee
        trulii_fee = base * fees.get('trulii')
        trulii_tax_fee = trulii_fee * IVA
        trulii_total_fee = trulii_fee + trulii_tax_fee

        # If organizer is major contributor, substract reteica and reteiva
        if regimen == OrganizerBankInfo.MAJOR_CONTIBUTOR:
            reteiva = fees.get('reteiva') * trulii_tax_fee
            reteica = fees.get('reteica_num') * trulii_fee / fees.get('reteica_den')
            trulii_total_fee -= reteica + reteiva

        # PayU fee
        payu_fee = base * fees.get('payu_fee_percentage') + fees.get('payu_fee_fixed')
        payu_tax_fee = IVA * payu_fee
        payu_trulii_tax_fee = fees.get('iva_trulii_payu') * trulii_tax_fee
        payu_total_fee = payu_fee + payu_tax_fee + payu_trulii_tax_fee

        # Add ICA and Renta if the payment was made with credit card

        if payment_type == Payment.CC_PAYMENT_TYPE:
            renta = fees.get('renta') * base
            ica = fees.get('ica') * base
            payu_total_fee += renta + ica

        total_fee = payu_total_fee + trulii_total_fee
        final_total = base - total_fee

        fee_detail = {
            'trulii_fee': trulii_fee,
            'trulii_tax_fee': trulii_tax_fee,
            'trulii_total_fee': trulii_total_fee,
            'reteiva': reteiva,
            'reteica': reteica,
            'payu_fee': payu_fee,
            'payu_tax_fee': payu_tax_fee,
            'payu_trulii_tax_fee': payu_trulii_tax_fee,
            'payu_total_fee': payu_total_fee,
            'renta': renta,
            'ica': ica,
            'total_fee': total_fee,
            'regimen': regimen,
            'payment_type': payment_type,
            'final_total': final_total
        }

        fee_detail.update({key: round(value, 2) 
                           for key, value in fee_detail.items() 
                           if  isinstance(value, numbers.Real)})

        return fee_detail


class Assistant(Tokenizable):
    order = models.ForeignKey(Order, related_name='assistants')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    enrolled = models.BooleanField(default=True)

    objects = AssistantQuerySet.as_manager()

    def save(self, *args, **kwargs):
        is_enrolled = self.enrolled
        order = self.order
        if self.pk is not None:

            was_enrolled = Assistant.objects.get(pk=self.pk).enrolled
            
            if not was_enrolled == is_enrolled:
                if is_enrolled and order.status in [order.ORDER_APPROVED_STATUS,
                                                         order.ORDER_PENDING_STATUS]:
                    order.calendar.decrease_capacity(1)
                elif not is_enrolled:
                    order.calendar.increase_capacity(1)
        else:
            if is_enrolled and order.status in [order.ORDER_APPROVED_STATUS,
                                                     order.ORDER_PENDING_STATUS]:

                order.calendar.decrease_capacity(1)


        super(Assistant, self).save(*args,**kwargs)



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
