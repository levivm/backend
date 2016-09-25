from django.contrib.postgres.fields import JSONField
from django.db import models


class Payment(models.Model):
    CC_PAYMENT_TYPE = 'CC'
    PSE_PAYMENT_TYPE = 'PSE'
    PAYMENT_TYPE = (
        (PSE_PAYMENT_TYPE, 'PSE'),
        (CC_PAYMENT_TYPE, 'Crédito')
    )
    CARD_TYPE = (
        ('visa', 'VISA'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('diners', 'Diners'),
    )
    date = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(choices=PAYMENT_TYPE, max_length=10)
    card_type = models.CharField(choices=CARD_TYPE, max_length=25)
    transaction_id = models.CharField(max_length=150)
    last_four_digits = models.CharField(max_length=5)
    response = JSONField(null=True)


class Fee(models.Model):

    TRULII = 'trulii'
    IVA = 'iva'
    PAYU_FEE_PERCENTAGE = 'payu_fee_percentage'
    PAYU_FEE_FIXED = 'payu_fee_fixed'
    RENTA = 'renta'
    ICA = 'ica'
    IVA_TRULII_PAYU = 'iva_trulii_payu'
    RETEICA_NUM = 'reteica_num'
    RETEICA_DEN = 'reteica_den'
    RETEIVA = 'reteiva'

    CHOICES_TYPE = (
        (TRULII, 'Comisión Trulii'),
        (IVA, 'IVA'),
        (PAYU_FEE_PERCENTAGE, 'Comisión PayU porcentual'),
        (PAYU_FEE_FIXED, 'Comisión PayU fija'),
        (RENTA, 'Descuento de Retención Renta'),
        (ICA, 'Descuento de Retención ICA'),
        (IVA_TRULII_PAYU, 'Comisión PayU IVA Trulii'),
        (RETEICA_NUM, 'Reteica Numerador'),
        (RETEICA_DEN, 'Reteica Denominador'),
        (RETEIVA, 'Reteiva'),
    )

    amount = models.FloatField()
    type = models.CharField(choices=CHOICES_TYPE, blank=True, max_length=100)

    def __str__(self):
        return '%s: %s' % (self.amount, self.type)

    @classmethod
    def get_fees_dict(cls):
        fee_types = cls.CHOICES_TYPE
        fees_dict = {}

        for type in fee_types:
            fee_amount = cls.objects.get(type=type[0]).amount
            fees_dict.update({type[0]: fee_amount})

        return fees_dict
