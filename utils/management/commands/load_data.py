from django.core.management.base import BaseCommand
from activities.management.commands import load_categories_and_subs, load_stock_covers
from locations.management.commands import load_cities
from payments.management.commands import load_fee
from users.management.commands import set_permissions
from referrals.management.commands import load_coupons


class Command(BaseCommand):
    help = "Load categories, subcategorias, cities and socialapp data"

    def handle(self, *args, **options):
        load_categories_and_subs.Command().load_categories_and_subcategories()
        load_cities.Command().load_cities()
        set_permissions.Command().set_permissions()
        load_fee.Command().handle()
        load_stock_covers.Command().handle()
        load_coupons.Command().handle()
