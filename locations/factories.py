import factory
import factory.fuzzy

from locations.models import City, Location


def get_point():
    latitude = factory.Faker('latitude').generate({})
    longitude = factory.Faker('longitude').generate({})

    return 'POINT(%s %s)' % (longitude, latitude)

class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City
        django_get_or_create = ('name',)

    name = factory.Faker('city')
    order = factory.Sequence(lambda n: '%d' % n)
    point = factory.fuzzy.FuzzyAttribute(get_point)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    address = factory.Faker('address')
    city = factory.SubFactory(CityFactory)
    point = factory.fuzzy.FuzzyAttribute(get_point)
