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

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_set_decline(self, send_mail):
        """
        Test the action set_decline
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.refunds[0].user.email,
            'status': 'sent',
            'reject_reason': None
        }]

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

    @mock.patch('orders.tasks.SendEmailOrganizerRefundTask.delay')
    @mock.patch('orders.tasks.SendEMailStudentRefundTask.delay')
    def test_set_approved(self, student_task, organizer_task):
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
        self.assertEqual(refund_2.order.status, Order.ORDER_CANCELLED_STATUS)
        self.assertFalse(refund_2.assistant.enrolled)
