import hashlib
import json
from django.conf import settings
from requests.api import post
from activities.models import Chronogram
from payments.models import Payment as PaymentModel


class PaymentUtil(object):
    def __init__(self, request, activity):
        super(PaymentUtil, self).__init__()
        self.request = request
        self.activity = activity
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}

    def get_signature(self, reference_code, price):
        signature = hashlib.md5()
        signature_data = {
            'apikey': settings.PAYU_API_KEY,
            'merchant_id': settings.PAYU_MERCHANT_ID,
            'reference_code': reference_code,
            'tx_value': price,
            'currency': 'COP',
        }
        signature_string = '{apikey}~{merchant_id}~{reference_code}~{tx_value}~{currency}'.format(**signature_data)
        signature.update(bytes(signature_string, 'utf8'))
        return signature.hexdigest()

    def get_amount(self):
        id = self.request.data.get('chronogram')
        chronogram = Chronogram.objects.get(id=id)
        return chronogram.session_price * self.request.data['quantity']

    def get_buyer(self):
        data = self.request.data.get('buyer')
        return {
            'fullName': data['name'],
            'emailAddress': data['email'],
        }

    def get_creditcard_association(self):
        return self.request.data['card_association'].upper()

    def get_payu_data(self):
        amount = self.get_amount()
        reference_code = self.get_reference_code()
        return {
            'language': 'es',
            'command': 'SUBMIT_TRANSACTION',
            'merchant': {
                'apiLogin': settings.PAYU_API_LOGIN,
                'apiKey': settings.PAYU_API_KEY,
            },
            'transaction': {
                'order': {
                    'accountId': '500538',
                    'referenceCode': reference_code,
                    'description': self.activity.short_description,
                    'language': 'es',
                    'signature': self.get_signature(reference_code=reference_code, price=amount),
                    'buyer': self.get_buyer(),
                    'additionalValues': {
                        'TX_VALUE': {
                            'value': amount,
                            'currency': 'COP'
                        }
                    },
                },
                'creditCardTokenId': self.request.data['token'],
                'type': 'AUTHORIZATION_AND_CAPTURE',
                'paymentMethod': self.card_association,
                'paymentCountry': 'CO',
            },
            'test': settings.PAYU_TEST
        }

    def creditcard(self):
        self.card_association = self.get_creditcard_association()
        payu_data = json.dumps(self.get_payu_data())
        result = post(url=settings.PAYU_URL, data=payu_data, headers=self.headers)
        result = result.json()
        if settings.PAYU_TEST:
            result = self.test_response(result)
        return self.response(result)

    def get_reference_code(self):
        reference = self.activity.title.replace(' ', '')
        return reference.lower()

    def response(self, result):
        if result['code'] == 'SUCCESS':
            payment_data = {
                'payment_type':' credit',
                'card_type': self.card_association.lower(),
                'transaction_id': result['transactionResponse']['transactionId'],
            }
            if result['transactionResponse']['state'] == 'APPROVED':
                payment = PaymentModel.objects.create(**payment_data)
                return {
                    'status': 'APPROVED',
                    'payment': payment,
                }
            elif result['transactionResponse']['state'] == 'PENDING':
                payment = PaymentModel.objects.create(**payment_data)
                return {
                    'status': 'PENDING',
                    'payment': payment,
                }
            else:
                return {
                    'status': 'ERROR',
                    'error': 'ERROR',
                }
        else:
            return {
                'status': 'ERROR',
                'error': 'ERROR'
            }

    def test_response(self, result):
        if self.request.data['buyer']['name'] == 'APPROVED':
            result['code'] = 'SUCCESS'
            result['transactionResponse']['state'] = 'APPROVED'
        elif self.request.data['buyer']['name'] == 'REJECTED':
            result['code'] = 'SUCCESS'
            result['transactionResponse']['state'] = 'DECLINED'
        elif self.request.data['buyer']['name'] == 'PENDING':
            result['code'] = 'SUCCESS'
            result['transactionResponse']['state'] = 'DECLINED'

        return result