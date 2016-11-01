from django.core import management
from rest_framework.test import APITestCase
from activities.management.commands.load_stock_covers import Command as LoadStockCoversCommand

from activities.models import SubCategory, ActivityStockPhoto


class LoadStockCoverTestCase(APITestCase):
    """
    Class to test the command load_stock_cover
    """

    def setUp(self):
        management.call_command('load_categories_and_subs')

    def test_command(self):
        """
        test command load_stock_cover
        """

        management.call_command('load_stock_covers')

        subcategories = SubCategory.objects.all()

        MAPPING = LoadStockCoversCommand.get_data()

        for subcategory in subcategories:
            self.assertEqual(ActivityStockPhoto.objects.filter(sub_category=subcategory).count(),
                             MAPPING[subcategory.category.name][subcategory.name])
