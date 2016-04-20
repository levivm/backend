import factory

from activities.factories import CalendarFactory
from balances.models import Balance, BalanceLog
from organizers.factories import OrganizerFactory


class BalanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Balance

    organizer = factory.SubFactory(OrganizerFactory)


class BalanceLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BalanceLog

    organizer = factory.SubFactory(OrganizerFactory)
    calendar = factory.SubFactory(CalendarFactory)
