from rest_framework.test import APITestCase

from payments.factories import PaymentFactory
from payments.serializers import PaymentSerializer


class PaymentSerializerTest(APITestCase):
    """
    Class for testing the PaymentSerializer serializer
    """

    def setUp(self):
        self.payment = PaymentFactory()

    def test_read(self):
        """
        Test the serializer's data returned
        """

        content = {
            'date': self.payment.date.isoformat()[:-6] + 'Z',
            'payment_type': self.payment.get_payment_type_display(),
            'card_type': self.payment.get_card_type_display(),
            'last_four_digits': str(self.payment.last_four_digits),
        }

        serializer = PaymentSerializer(self.payment)
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))
