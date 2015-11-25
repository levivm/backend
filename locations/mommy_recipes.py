from model_mommy.recipe import Recipe, seq, foreign_key
from faker import Faker
from locations.models import City, Location
from organizers.mommy_recipes import organizer

fake = Faker()

def get_point():
    return '(%s, %s)' % (fake.latitude(), fake.longitude())

city = Recipe(
    City,
    name=fake.city,
    order=seq(0),
    point=get_point,
)

location = Recipe(
    Location,
    address=fake.address, #models.TextField()
    city=foreign_key(city), #models.ForeignKey(City)
    point=get_point, #models.CharField(max_length="200")
    organizer=foreign_key(organizer), #models.ForeignKey(Organizer,null=True,related_name="locations")
)
