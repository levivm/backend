from django.core.management.base import BaseCommand

from locations.models import City


class Command(BaseCommand):
    help = "Create cities"

    def handle(self, *args, **options):
        self.load_cities()

    def load_cities(self, *args, **options):
        data = self.get_data()
        _cities = map(lambda x: City(name=x['name'], point=x['point']), data)
        City.objects.bulk_create(_cities)

    def get_data(self):
        return [
            {
                "name": "Bogotá",
                "point": "POINT(4.5980478 -74.0760867)"
            },

        ]
