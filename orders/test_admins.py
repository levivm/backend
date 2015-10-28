from django.conf import settings
import mock
from django.contrib.admin.sites import AdminSite
from model_mommy import mommy
from rest_framework.test import APITestCase
from orders.admin import RefundAdmin
from orders.models import Refund
from utils.models import EmailTaskRecord


class RefundAdminTest(APITestCase):
    """
    Class to test the RefundAdmin
    """

    def setUp(self):
        self.admin = RefundAdmin(Refund, AdminSite())
        self.refunds = mommy.make(Refund, _quantity=2)

        settings.CELERY_ALWAYS_EAGER = True

    def test_set_decline(self):
        """
        Test the action set_decline
        """

        email_counter = EmailTaskRecord.objects.count()
        queryset = Refund.objects.filter(id=self.refunds[0].id)
        request = mock.Mock()
        self.admin.set_decline(request, queryset)

        self.assertEqual(Refund.objects.get(id=self.refunds[0].id).status, Refund.DECLINED_STATUS)
        self.assertEqual(Refund.objects.get(id=self.refunds[1].id).status, Refund.PENDING_STATUS)
        self.assertEqual(EmailTaskRecord.objects.count(), email_counter + 1)
