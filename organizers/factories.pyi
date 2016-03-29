import factory

from organizers.models import Organizer


class OrganizerFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Organizer: ...
