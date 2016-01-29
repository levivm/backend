import random

import factory

from referrals.models import Referral, CouponType, Coupon, Redeem
from students.factories import StudentFactory


class ReferralFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Referral

    def __new__(cls, *args, **kwargs):
        return super(ReferralFactory, cls).__new__(*args, **kwargs)

    referred = factory.SubFactory(StudentFactory)
    referrer = factory.SubFactory(StudentFactory)
    ip_address = factory.Faker('ipv4')


class CouponTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CouponType

    name = factory.LazyAttribute(lambda ct: 'coupon %d' % (CouponType.objects.count() + 1))
    amount = factory.LazyAttribute(lambda ct: random.choice(range(100000, 500000)))
    type = factory.LazyAttribute(lambda ct: random.choice([k for k, v in CouponType.TYPES]))


class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coupon

    coupon_type = factory.SubFactory(CouponTypeFactory)


class RedeemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Redeem

    def __new__(cls, *args, **kwargs):
        return super(RedeemFactory, cls).__new__(*args, **kwargs)

    student = factory.SubFactory(StudentFactory)
    coupon = factory.SubFactory(CouponFactory)
