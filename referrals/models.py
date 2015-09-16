from random import sample
from string import ascii_uppercase
from django.db import models
from students.models import Student


class Referral(models.Model):
    referred = models.ForeignKey(Student, related_name='referreds')
    referrer = models.ForeignKey(Student, related_name='referrers')
    ip_address = models.GenericIPAddressField()


class Coupon(models.Model):
    TYPES = (
        ('global', 'Global'),
        ('referral', 'Referral'),
    )
    CODE_SIZE = 5

    redeems = models.ManyToManyField(Student, through='Redeem')
    code = models.CharField(max_length=15, unique=True)
    amount = models.IntegerField()
    coupon_type = models.CharField(choices=TYPES, default='referral', max_length=15)

    def save(self, *args, **kwargs):
        if not self.id:
            self.code = self.generate_code()
        super(Coupon, self).save(*args, **kwargs)

    def generate_code(self):
        code = ''.join(sample(ascii_uppercase, self.CODE_SIZE))

        while Coupon.objects.filter(code='%s-%s' % (self.coupon_type.upper(), code)).exists():
            code = ''.join(sample(ascii_uppercase, self.CODE_SIZE))

        return '%s-%s' % (self.coupon_type.upper(), code)

    def __str__(self):
        return self.code


class Redeem(models.Model):
    student = models.ForeignKey(Student)
    coupon = models.ForeignKey(Coupon)
    used = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
