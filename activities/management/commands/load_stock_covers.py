from activities.models import Category,SubCategory,ActivityStockPhoto
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create categories and subcategories covers photo"

    def handle(self, *args, **options):
        self.create_covers()

    def create_covers(self):
        # queryset = SubCategory.objects.filter(name='Yoga')
        subcategories = SubCategory.objects.all()
        # if queryset:
        #   yoga_sc = list(queryset).pop()
        for subcategory in subcategories:
            for index in range(0,5):
                photo = "activities/Yoga---Homepage-02.jpg"
                asp = ActivityStockPhoto(sub_category=subcategory)
                asp.photo = photo
                asp.save()



