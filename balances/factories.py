import factory

from activities.factories import CalendarFactory
from balances.models import Balance, BalanceLog, Withdrawal
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


class WithdrawalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Withdrawal

    organizer = factory.SubFactory(OrganizerFactory)
    amount = factory.Faker('random_int', min=100000, max=999999)

    @factory.post_generation
    def logs(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for log in extracted:
                self.logs.add(log)
