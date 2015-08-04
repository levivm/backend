from allauth.socialaccount.models import SocialApp
from django.core.management.base import BaseCommand, CommandError
from activities.management.commands import load_categories_and_subs
from locations.management.commands import load_cities
from utils.management.commands import load_socialapp

class Command(BaseCommand):
    help = "Load categories, subcategorias, cities and socialapp data"

    def handle(self, *args, **options):
        load_categories_and_subs.Command().load_categories_and_subcategories()
        load_cities.Command().load_cities()
        load_socialapp.Command().load_socialapp()