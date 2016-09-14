from django.core.management.base import BaseCommand

from payments.models import Fee


class Command(BaseCommand):
    help = "Create initial fee"

    def handle(self, *args, **options):
        Fee.objects.get_or_create(name='trulii', amount=0.08)
        Fee.objects.get_or_create(name='IVA', amount=0.16)
