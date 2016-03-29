import factory

from reviews.models import Review


class ReviewFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Review:...
