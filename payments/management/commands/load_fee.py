from django.core.management.base import BaseCommand

from payments.models import Fee


class Command(BaseCommand):
    help = "Create initial fee"

    def handle(self, *args, **options):

        fee_choices = {
            'trulii': 0.035,
            'iva': 0.16,
            'payu_fee_percentage': 0.0349,
            'payu_fee_fixed': 900.0,
            'renta': 0.015,
            'ica': 0.00414,
            'iva_trulii_payu': 0.15,
            'reteica_num': 11.04,
            'reteica_den': 1000,
            'reteiva': 0.15,
        }

        fee_types = Fee.CHOICES_TYPE

        for c in fee_types:
            if c[0] not in fee_choices.keys():
                raise Exception('No hay un fee presente')
            Fee.objects.update_or_create(type=c[0], defaults={'amount': fee_choices.get(c[0])})
