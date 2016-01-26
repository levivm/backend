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
    amount = models.FloatField()
    name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return '%s: %s' % (self.amount, self.name)
