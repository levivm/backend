from rest_framework.test import APITestCase
from django.db.models import Q
from .searchs import OrderSearchEngine
from datetime import datetime
import time

class OrderSearchEngineTest(APITestCase):
    """
    Class for testing the OrderSearchEngine
    """

    def setUp(self):
        # Arrangement
        self.today = time.time()*1000
        self.from_date = datetime.fromtimestamp(int(self.today)// 1000).\
                                          replace(second=0).date()
        self.until_date = datetime.fromtimestamp(int(self.today)// 1000).\
                                          replace(second=0).date()
        self.final_price = 100000

    def test_from_date(self):
        """
        Test the filter_query method with from_date param
        """

        query_params = {
            'from_date': self.today,
        }
        search = OrderSearchEngine()
        query = search.filter_query(query_params)
        content = Q(created_at__gte=self.from_date)
        self.assertEqual(str(query), str(content))

    def test_until_date(self):
        """
        Test the filter_query method with until_date param
        """

        query_params = {
            'until_date': self.today,
        }
        search = OrderSearchEngine()
        query = search.filter_query(query_params)
        content = Q(created_at__lte=self.until_date)
        self.assertEqual(str(query), str(content))

    def test_date_rage(self):
        """
        Test the filter_query method with until_date param
        """

        query_params = {
            'until_date': self.today,
            'from_date': self.today,
        }
        search = OrderSearchEngine()
        query = search.filter_query(query_params)
        content = Q(created_at__range=[self.from_date, self.until_date])
        self.assertEqual(str(query), str(content))

    #     query_params = {
    #         'cost_start': self.initial_price,
    #         'cost_end': settings.PRICE_RANGE.get('max'),
    #     }



    # def test_filter_query_price_ranges(self):
    #     """
    #     Test the filter_query method with price ranges
    #     """

    #     # Without limit
    #     query_params = {
    #         'cost_start': self.initial_price,
    #         'cost_end': settings.PRICE_RANGE.get('max'),
    #     }

    #     search = ActivitySearchEngine()
    #     query = search.filter_query(query_params=query_params)
    #     content = Q(published=True) & Q(calendars__session_price__gte=self.initial_price)

    #     self.assertEqual(str(query), str(content))

    #     # With limit
    #     query = search.filter_query(query_params={**query_params, 'cost_end': self.final_price})
    #     content = Q(published=True) & Q(calendars__session_price__range=(self.initial_price, self.final_price))

    #     self.assertEqual(str(query), str(content))