from django.contrib.auth.models import User
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from orders.models import Order, Assistant, Refund
from orders.serializers import RefundSerializer


class RefundSerializerTest(APITestCase):
    """
    Class to test the serializer RefundSerializer
    """

    def setUp(self):
        # Arrangement
        self.user = mommy.make(User)
        self.assistant = mommy.make(Assistant)

    def test_create(self):
        """
        Test creation of a RefundOrder
        """

        data = {
            'user': self.user.id,
            'assistant': self.assistant.id,
            'order': self.assistant.order.id,
        }

        serializer = RefundSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        content = {'id': 1, 'user_id': self.user.id, 'assistant_id': self.assistant.id, 'status': 'pending'}

        self.assertTrue(set(content).issubset(instance.__dict__))

    def test_update(self):
        """
        Test update of a RefundOrder
        """

        # Arrangement
        refund_assistant = mommy.make(Refund, user=self.user)

        data = {'status': 'approved'}
        serializer = RefundSerializer(refund_assistant, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        content = refund_assistant.__dict__
        content.update({'status': 'approved'})

        self.assertEqual(refund_assistant.id, instance.id)
        self.assertEqual(content, instance.__dict__)
#
    def test_validation(self):
        """
        Test validation
        """

        data = {
            'user': 1,
            'order': self.assistant.order.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

        self.assertEqual(Refund.objects.count(), 0)
