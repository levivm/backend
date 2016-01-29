import factory

from referrals.models import Referral, Redeem


class ReferralFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Referral: ...


class RedeemFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Redeem: ...
