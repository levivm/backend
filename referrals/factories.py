import random

import factory

from referrals.models import Referral, CouponType, Coupon, Redeem
from students.factories import StudentFactory


class ReferralFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Referral

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

    student = factory.SubFactory(StudentFactory)
    coupon = factory.SubFactory(CouponFactory)
    used = factory.Faker('boolean')
