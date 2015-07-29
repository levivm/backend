from django.db import models


class Payment(models.Model):
    PAYMENT_TYPE = (
        ('debit', 'Débito'),
        ('credit', 'Crédito')
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
