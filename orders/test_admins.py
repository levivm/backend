import mock

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from model_mommy import mommy
from rest_framework.test import APITestCase
from orders.admin import RefundAdmin
from orders.models import Refund, Order, Assistant
from utils.models import EmailTaskRecord


class RefundAdminTest(APITestCase):
    """
    Class to test the RefundAdmin
    """

    def setUp(self):
        self.admin = RefundAdmin(Refund, AdminSite())
        self.refunds = mommy.make(Refund, _quantity=2, order__status=Order.ORDER_APPROVED_STATUS)

        settings.CELERY_ALWAYS_EAGER = True

    def test_set_decline(self):
        """
        Test the action set_decline
        """

        # Counter
        email_counter = EmailTaskRecord.objects.count()

        # Arrangement
        # Set the parameters and call the method
        queryset = Refund.objects.filter(id=self.refunds[0].id)
        request = mock.Mock()
        self.admin.set_declined(request, queryset)

        # Reload refunds data
        refund_1, refund_2 = Refund.objects.order_by('pk')

        self.assertEqual(refund_1.status, Refund.DECLINED_STATUS)
        self.assertEqual(refund_2.status, Refund.PENDING_STATUS)
        self.assertEqual(EmailTaskRecord.objects.count(), email_counter + 1)

    def test_set_approved(self):
        """
        Test the action set_approved
        """

        # Counter
        email_counter = EmailTaskRecord.objects.count()

        # Arrangement
        # Assign an assistant to the second refund
        self.refunds[1].assistant = mommy.make(Assistant, order=self.refunds[1].order)
        self.refunds[1].save()

        # Set the parameters and call the method
        queryset = Refund.objects.all()
        request = mock.Mock()
        self.admin.set_approved(request, queryset)

        # Reload refunds data
        refund_1, refund_2 = Refund.objects.order_by('pk')

        self.assertEqual(refund_1.status, Refund.APPROVED_STATUS)
        self.assertEqual(refund_1.order.status, Order.ORDER_CANCELLED_STATUS)
        self.assertEqual(refund_2.order.status, Order.ORDER_APPROVED_STATUS)
        self.assertFalse(refund_2.assistant.enrolled)
        self.assertEqual(EmailTaskRecord.objects.count(), email_counter + 4)
