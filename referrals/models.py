from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from students.models import Student
from utils.behaviors import Tokenizable


class Referral(models.Model):
    referred = models.ForeignKey(Student, related_name='referreds')
    referrer = models.ForeignKey(Student, related_name='referrers')
    ip_address = models.GenericIPAddressField()


class CouponType(models.Model):
    TYPES = (
        ('global', 'Global'),
        ('referral', 'Referral'),
    )

    name = models.CharField(max_length=20, unique=True)
    amount = models.IntegerField()
    type = models.CharField(choices=TYPES, default='referral', max_length=15)

    def __str__(self):
        return self.name


# class RedeemQuerySet(models.QuerySet):
#     def globals(self, *args, **kwargs):
#         return self.filter(coupon_type='global', *args, **kwargs)
#
#     def referrals(self, *args, **kwargs):
#         return self.filter(coupon_type='referral', *args, **kwargs)


class Coupon(Tokenizable):
    redeems = models.ManyToManyField(Student, through='Redeem')
    coupon_type = models.ForeignKey(CouponType)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)

    # objects = RedeemQuerySet.as_manager()

    def generate_token(self, *args, **kwargs):
        return super(Coupon, self).generate_token(prefix=self.coupon_type.type.upper())

    def is_valid(self, student):
        params = {
            'student': student,
            'coupon': self,
        }

        error_message = _('The coupon is not valid.')
        if self.coupon_type.type == 'global':
            if Redeem.objects.filter(used=True, **params).exists():
                raise serializers.ValidationError(error_message)
        else:
            if not Redeem.objects.filter(used=False, **params).exists():
                raise serializers.ValidationError(error_message)

    def set_used(self, student):
        if self.coupon_type.type == 'referral':
            redeem = self.redeem_set.get(student=student)
            redeem.set_used()
        else:
            Redeem.objects.create(
                student=student,
                coupon=self,
                used=True,
                redeem_at=now()
            )

class Redeem(models.Model):
    student = models.ForeignKey(Student)
    coupon = models.ForeignKey(Coupon)
    used = models.BooleanField(default=False)
    redeem_at = models.DateTimeField(blank=True, null=True)

    def set_used(self):
        self.used = True
        self.redeem_at = now()
        self.save(update_fields=['used', 'redeem_at'])
