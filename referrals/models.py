from django.db import models

from students.models import Student
from utils.behaviors import Tokenizable


class Referral(models.Model):
    referred = models.ForeignKey(Student, related_name='referreds')
    referrer = models.ForeignKey(Student, related_name='referrers')
    ip_address = models.GenericIPAddressField()


class Coupon(models.Model):
    TYPES = (
        ('global', 'Global'),
        ('referral', 'Referral'),
    )

    redeems = models.ManyToManyField(Student, through='Redeem')
    name = models.CharField(max_length=20, unique=True)
    amount = models.IntegerField()
    coupon_type = models.CharField(choices=TYPES, default='referral', max_length=15)


class Redeem(Tokenizable):
    student = models.ForeignKey(Student)
    coupon = models.ForeignKey(Coupon)
    used = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_used = models.DateField(editable=False, null=True)

    def generate_token(self, *args, **kwargs):
        return super(Redeem, self).generate_token(prefix=self.coupon.coupon_type.upper())
