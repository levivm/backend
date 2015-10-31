from allauth.socialaccount.models import SocialApp
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Create cities"

    def handle(self, *args, **options):
        self.load_socialapp()



    def load_socialapp(self,*args, **options):
        data = self.get_data()
        site = Site.objects.get(id=1)

        social_app = SocialApp.objects.create(**data)
        social_app.sites.add(site)
        social_app.save()

    def get_data(self):
        return  {
            "name": "trulii",
            "client_id":"1563536137193781",
            "secret":"9fecd238829796fd99109283aca7d4ff",
            "provider":"facebook",
        }