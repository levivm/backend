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

        search = ActivitySearchEngine(query_params=query_params)
        query = search.filter_query()
        content = Q(published=True) & (Q(calendars__session_price__gte=self.initial_price) | Q(calendars__packages__price__gte=50000))

        self.assertEqual(str(query), str(content))

        # With limit
        search = ActivitySearchEngine(query_params={**query_params, 'cost_end': self.final_price})
        query = search.filter_query()
        content = Q(published=True) & (Q(calendars__session_price__range=(self.initial_price, self.final_price)) | Q(calendars__packages__price__range=(50000, 100000)))

        self.assertEqual(str(query), str(content))
