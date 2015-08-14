from locations.models import City
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create cities"

    def handle(self, *args, **options):
        self.load_cities()



    def load_cities(self,*args, **options):
        data = self.get_data()
        _cities = map(lambda x:City(name=x['name'],point=x['point']),data)
        City.objects.bulk_create(_cities)





    def get_data(self):
        return [
            {
                "name":"Bogotá",
                "point":"(4.5981, -74.0758)"

            },
            {
                "name":"Barranquilla",
                "point":"(4.5981, -74.0758)"

            },

        ]