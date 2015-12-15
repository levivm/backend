from django.conf import settings
from django.db.models import Q
from rest_framework.test import APITestCase

from activities.searchs import ActivitySearchEngine


class ActivitySearchEngineTest(APITestCase):
    """
    Class for testing the ActivitySearchEngine
    """

    def setUp(self):
        # Arrangement
        self.initial_price = 50000
        self.final_price = 100000

    def test_filter_query_price_ranges(self):
        """
        Test the filter_query method with price ranges
        """

        # Without limit
        query_params = {
            'cost_start': self.initial_price,
            'cost_end': settings.PRICE_RANGE.get('max'),
        }

        search = ActivitySearchEngine()
        query = search.filter_query(query_params=query_params)
        content = Q(published=True) & Q(calendars__session_price__gte=self.initial_price)

        self.assertEqual(str(query), str(content))

        # With limit
        query = search.filter_query(query_params={**query_params, 'cost_end': self.final_price})
        content = Q(published=True) & Q(calendars__session_price__range=(self.initial_price, self.final_price))

        self.assertEqual(str(query), str(content))
