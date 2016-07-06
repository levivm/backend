from django.core.management.base import BaseCommand

from referrals.models import CouponType


class Command(BaseCommand):
    help = "Create initial cuopons"

    def get_coupons_data(self):
        return [{
            'name': 'referred',
            'type': 'referral',
            'amount': 20000
        }, {
            'name': 'referrer',
            'type': 'referral',
            'amount': 20000
        }]

    def handle(self, *args, **options):
        [CouponType.objects.get_or_create(**data) for data in self.get_coupons_data()]
