from django.db import models
from django.utils.translation import ugettext as _

from activities.models import Calendar
from balances.querysets import BalanceLogQuerySet
from organizers.models import Organizer


class Balance(models.Model):
    organizer = models.OneToOneField(Organizer, related_name='balance')
    available = models.FloatField(default=0)
    unavailable = models.FloatField(default=0)


class BalanceLog(models.Model):

    STATUS_AVAILABLE = 'available'
    STATUS_UNAVAILABLE = 'unavailable'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_REQUESTED = 'requested'

    STATUS = (
        (STATUS_AVAILABLE, _('Disponible')),
        (STATUS_UNAVAILABLE, _('No Disponible')),
        (STATUS_WITHDRAWN, _('Retirado')),
        (STATUS_REQUESTED, _('Solicitado')),
    )

    organizer = models.ForeignKey(Organizer, related_name='balance_logs')
    calendar = models.ForeignKey(Calendar, related_name='balance_logs')
    status = models.CharField(choices=STATUS, max_length=15, default='unavailable')

    objects = BalanceLogQuerySet.as_manager()

    @classmethod
    def create(cls, organizer=None, calendar=None):
        instance, created = cls.objects.get_or_create(organizer=organizer, calendar=calendar)
        return instance



class Withdrawal(models.Model):
    STATUS = (
        ('pending', _('Pendiente')),
        ('approved', _('Aprobado')),
        ('declined', _('Rechazado')),
    )
    organizer = models.ForeignKey(Organizer, related_name='withdrawals')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(default=0)
    status = models.CharField(choices=STATUS, max_length=10, default='pending')
    logs = models.ManyToManyField(BalanceLog, related_name='withdraws')
