from activities.models import SubCategory, ActivityStockPhoto
from django.core.management.base import BaseCommand
from activities.management.commands.load_categories_and_subs import Command as CommandCategories


class Command(BaseCommand):
    help = "Create categories and subcategories covers photo"

    @staticmethod
    def get_data():
        data = CommandCategories.get_data()
        data = {key: {subcategory: 5 for subcategory in data.get(key).get('subcategories')} for key in data.keys()}
        return data

    def handle(self, *args, **options):
        subcategories = SubCategory.objects.all()
        MAPPING = Command.get_data()
        for subcategory in subcategories:
            category = subcategory.category
            try:
                MAPPING[category.name][subcategory.name]
            except KeyError:

                pass
            for index in range(1, MAPPING[category.name][subcategory.name] + 1):

                
                data = {
                    'category': category.name,
                    'subcategory': subcategory.name,
                    'filename': '%s %02i.jpg' % (subcategory.name, index)
                }
                filepath = 'activities_stock/%(category)s/%(subcategory)s/%(filename)s' % data
                ActivityStockPhoto.objects.create(sub_category=subcategory, photo=filepath)
