from allauth.socialaccount.models import SocialApp
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create cities"

    def handle(self, *args, **options):
        self.load_socialapp()



    def load_socialapp(self,*args, **options):
        data = self.get_data()
        SocialApp.objects.create(**data)

    def get_data(self):
        return  {
            "name": "trulii",
            "client_id":"1563536137193781",
            "secret":"9fecd238829796fd99109283aca7d4ff",
            "provider":"facebook",
        }