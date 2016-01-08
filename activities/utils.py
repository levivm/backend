import calendar
import hashlib
import json

from django.conf import settings
from django.utils.timezone import now
from requests.api import post
from django.utils.translation import ugettext_lazy as _

from activities.models import Calendar
from utils.exceptions import ServiceUnavailable
from payments.serializers import PaymentsPSEDataSerializer
from payments.models import Payment as PaymentModel


class PaymentUtil(object):
    RESPONSE_CODE = {
        'ERROR': 'Ocurrió un error general.',
        'APPROVED': 'La transacción fue aprobada.',
        'ANTIFRAUD_REJECTED': 'La transacción fue rechazada por el sistema anti-fraude.',
        'PAYMENT_NETWORK_REJECTED': 'La red financiera rechazó la transacción.',
        'ENTITY_DECLINED': 'La transacción fue declinada por el banco o por la red financiera debido a un error.',
        'INTERNAL_PAYMENT_PROVIDER_ERROR': 'Ocurrió un error en el sistema intentando procesar el pago.',
        'INACTIVE_PAYMENT_PROVIDER': 'El proveedor de pagos no se encontraba activo.',
        'DIGITAL_CERTIFICATE_NOT_FOUND': 'La red financiera reportó un error en la autenticación.',
        'INVALID_EXPIRATION_DATE_OR_SECURITY_CODE': 'El código de seguridad o la fecha de expiración estaba inválido.',
        'INSUFFICIENT_FUNDS': 'La cuenta no tenía fondos suficientes.',
        'CREDIT_CARD_NOT_AUTHORIZED_FOR_INTERNET_TRANSACTIONS': 'La tarjeta de crédito no estaba autorizada para '
                                                                'transacciones por Internet.',
        'INVALID_TRANSACTION': 'La red financiera reportó que la transacción fue inválida.',
        'INVALID_CARD': 'La tarjeta es inválida.',
        'EXPIRED_CARD': 'La tarjeta ya expiró.',
        'RESTRICTED_CARD': 'La tarjeta presenta una restricción.',
        'CONTACT_THE_ENTITY': 'Debe contactar al banco.',
        'REPEAT_TRANSACTION': 'Se debe repetir la transacción.',
        'ENTITY_MESSAGING_ERROR': 'La red financiera reportó un error de comunicaciones con el banco.',
        'BANK_UNREACHABLE': 'El banco no se encontraba disponible.',
        'EXCEEDED_AMOUNT': 'La transacción excede un monto establecido por el banco.',
        'NOT_ACCEPTED_TRANSACTION': 'La transacción no fue aceptada por el banco por algún motivo.',
        'ERROR_CONVERTING_TRANSACTION_AMOUNTS': 'Ocurrió un error convirtiendo los montos a la moneda de pago.',
        'EXPIRED_TRANSACTION': 'La transacción expiró.',
        'PENDING_TRANSACTION_REVIEW': 'La transacción fue detenida y debe ser revisada, esto puede ocurrir por filtros '
                                      'de seguridad.',
        'PENDING_TRANSACTION_CONFIRMATION': 'La transacción está pendiente de ser confirmada.',
        'PENDING_TRANSACTION_TRANSMISSION': 'La transacción está pendiente para ser trasmitida a la red financiera. '
                                            'Normalmente esto aplica para transacciones con pago en efectivo.',
        'PAYMENT_NETWORK_BAD_RESPONSE': 'El mensaje retornado por la red financiera es inconsistente.',
        'PAYMENT_NETWORK_NO_CONNECTION': 'No se pudo realizar la conexión con la red financiera.',
        'PAYMENT_NETWORK_NO_RESPONSE': 'La red financiera no respondió.',
    }

    RESPONSE_CODE_NOTIFICATION_URL = {
        'ERROR': _('Ocurrió un error general.'),
        'APPROVED': _('La transacción fue aprobada.'),
        'ANTIFRAUD_REJECTED': _('La transacción fue rechazada por el sistema anti-fraude.'),
        'PAYMENT_NETWORK_REJECTED': _('La red financiera rechazó la transacción.'),
        'BANK_ACCOUNT_ACTIVATION_ERROR': _('Débito automático no permitido'),
        'BANK_ACCOUNT_NOT_AUTHORIZED_FOR_AUTOMATIC_DEBIT': _('Débito automático no permitido'),
        'INVALID_AGENCY_BANK_ACCOUNT': _('Débito automático no permitido'),
        'INVALID_BANK_ACCOUNT': _('Débito automático no permitido'),
        'INVALID_BANK': _('Débito automático no permitido'),
        'FIX_NOT_REQUIRED': _('Error'),
        'AUTOMATICALLY_FIXED_AND_SUCCESS_REVERSAL': _('Error'),
        'AUTOMATICALLY_FIXED_AND_UNSUCCESS_REVERSAL': _('Error'),
        'AUTOMATIC_FIXED_NOT_SUPPORTED': _('Error'),
        'NOT_FIXED_FOR_ERROR_STATE': _('Error'),
        'ERROR_FIXING_AND_REVERSING': _('Error'),
        'ERROR_FIXING_INCOMPLETE_DATA': _('Error'),
        'ABANDONED_TRANSACTION': _('Transacción abandonada por el pagador'),
        'ENTITY_DECLINED': _('La transacción fue declinada por el banco o por la red financiera debido a un error.'),
        'INTERNAL_PAYMENT_PROVIDER_ERROR': _('Ocurrió un error en el sistema intentando procesar el pago.'),
        'INACTIVE_PAYMENT_PROVIDER': _('El proveedor de pagos no se encontraba activo.'),
        'DIGITAL_CERTIFICATE_NOT_FOUND': _('La red financiera reportó un error en la autenticación.'),
        'INVALID_EXPIRATION_DATE_OR_SECURITY_CODE': _(
            'El código de seguridad o la fecha de expiración estaba inválido.'),
        'INSUFFICIENT_FUNDS': _('La cuenta no tenía fondos suficientes.'),
        'CREDIT_CARD_NOT_AUTHORIZED_FOR_INTERNET_TRANSACTIONS': _(
            'La tarjeta de crédito no estaba autorizada para transacciones por Internet.'),
        'INVALID_TRANSACTION': _('La red financiera reportó que la transacción fue inválida.'),
        'INVALID_CARD': _('La tarjeta es inválida.'),
        'EXPIRED_CARD': _('La tarjeta ya expiró.'),
        'RESTRICTED_CARD': _('La tarjeta presenta una restricción.'),
        'CONTACT_THE_ENTITY': _('Debe contactar al banco.'),
        'REPEAT_TRANSACTION': _('Se debe repetir la transacción.'),
        'ENTITY_MESSAGING_ERROR': _('La red financiera reportó un error de comunicaciones con el banco.'),
        'BANK_UNREACHABLE': _('El banco no se encontraba disponible.'),
        'EXCEEDED_AMOUNT': _('La transacción excede un monto establecido por el banco.'),
        'NOT_ACCEPTED_TRANSACTION': _('La transacción no fue aceptada por el banco por algún motivo.'),
        'ERROR_CONVERTING_TRANSACTION_AMOUNTS': _('Ocurrió un error convirtiendo los montos a la moneda de pago.'),
        'EXPIRED_TRANSACTION': _('La transacción expiró.'),
        'PAYMENT_NETWORK_BAD_RESPONSE': _('El mensaje retornado por la red financiera es inconsistente.'),
        'PAYMENT_NETWORK_NO_CONNECTION': _('No se pudo realizar la conexión con la red financiera.'),
        'PAYMENT_NETWORK_NO_RESPONSE': _('La red financiera no respondió.'),
    }

    card_association = None
    last_four_digits = None

    def __init__(self, request, activity=None, coupon=None):
        super(PaymentUtil, self).__init__()
        self.request = request
        if activity:
            self.activity = activity
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        self.coupon = coupon

    @staticmethod
    def get_signature(reference_code, price):
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

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_amount(self):
        calendar_id = self.request.data.get('calendar')
        calendar = Calendar.objects.get(id=calendar_id)
        quantity = int(self.request.data['quantity'])
        amount = calendar.session_price * quantity
        if self.coupon:
            amount -= self.coupon.coupon_type.amount
            amount = 0 if amount < 0 else amount
        return amount

    def get_buyer(self):
        data = self.request.data.get('buyer')
        return {
            'fullName': data['name'],
            'emailAddress': data['email'],
        }

    def get_payer(self):
        data = self.request.data.get('buyer')
        return {
            "fullName": data['name'],
            "emailAddress": data['payerEmail'],
            "contactPhone": data['contactPhone']
        }

    def get_extra_pse_parameters(self):
        data = self.request.data.get('buyer_pse_data')

        return {

            'FINANCIAL_INSTITUTION_CODE': data['bank'],
            'USER_TYPE': data['userType'],
            'PSE_REFERENCE1': self.get_client_ip(self.request),
            'PSE_REFERENCE3': data['idNumber'],

        }

    def get_creditcard_association(self):
        return self.request.data['card_association'].upper()

    def get_last_four_digits(self):
        return self.request.data['last_four_digits']

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
                    'accountId': settings.PAYU_ACCOUNT_ID,
                    'referenceCode': reference_code,
                    'description': self.get_payment_description(),
                    'language': 'es',
                    'notifyUrl': settings.PAYU_NOTIFY_URL,
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
                'userAgent': self.get_user_agent(),
                'deviceSessionId': self.get_device_session_id(),
                'cookie': self.get_cookie()

            },
            'test': settings.PAYU_TEST
        }

    def creditcard(self):
        self.card_association = self.get_creditcard_association()
        self.last_four_digits = self.get_last_four_digits()
        payu_data = json.dumps(self.get_payu_data())
        result = post(url=settings.PAYU_URL, data=payu_data, headers=self.headers)
        result = result.json()
        return self.response(result)

    def get_cookie(self):
        return self.request.auth.key

    def get_device_session_id(self):
        return self.request.data.get('deviceSessionId')

    def get_user_agent(self):
        return self.request.META.get('HTTP_USER_AGENT')

    def get_payment_description(self):
        description = "Inscripción de actividad {}".format(self.activity.title)
        description = str(_(description))
        return description

    def get_reference_code(self):
        activity_id = self.activity.id
        timestamp = calendar.timegm(now().timetuple())
        user_id = self.request.user.id
        calendar_id = self.request.data.get('calendar')
        reference = "{}-{}-{}-{}".format(timestamp, user_id, activity_id, calendar_id)
        return reference

    def response(self, result):

        if result['code'] == 'SUCCESS':
            payment_data = {
                'payment_type': 'CC',
                'card_type': self.card_association.lower(),
                'transaction_id': result['transactionResponse']['transactionId'],
                'last_four_digits': self.last_four_digits
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
                    'error': self.RESPONSE_CODE.get(result['transactionResponse']['responseCode'],
                                                    'Su tarjeta ha sido rechazada'),
                }
        else:
            return {
                'status': 'ERROR',
                'error': 'ERROR'
            }

    def pse_response(self, result):
        if result['code'] == 'SUCCESS':
            payment_data = {
                'payment_type': 'PSE',
                'transaction_id': result['transactionResponse']['transactionId'],
            }
            if result['transactionResponse']['state'] == 'PENDING':
                payment = PaymentModel.objects.create(**payment_data)
                return {
                    'status': 'PENDING',
                    'bank_url': result['transactionResponse']['extraParameters']['BANK_URL'],
                    'payment': payment,

                }
            else:

                return {
                    'status': 'ERROR',
                    'error': self.RESPONSE_CODE.get(result['transactionResponse']['responseCode'],
                                                    'Hubo un error al procesar su transacción'),
                }
        else:
            return {
                'status': 'ERROR',
                'error': 'ERROR'
            }

    def get_payu_pse_data(self):
        amount = self.get_amount()
        reference_code = self.get_reference_code()

        return {
            "language": "es",
            "command": "SUBMIT_TRANSACTION",
            'merchant': {
                'apiLogin': settings.PAYU_API_LOGIN,
                'apiKey': settings.PAYU_API_KEY,
            },
            "transaction": {
                "order": {
                    "accountId": settings.PAYU_ACCOUNT_ID,
                    "referenceCode": reference_code,
                    "description": self.get_payment_description(),
                    "language": "es",
                    "signature": self.get_signature(reference_code=reference_code, price=amount),
                    "notifyUrl": settings.PAYU_NOTIFY_URL,
                    "additionalValues": {
                        "TX_VALUE": {
                            "value": amount,
                            "currency": "COP"
                        }
                    },
                    "buyer": self.get_payer()
                },
                "payer": self.get_payer(),
                "extraParameters": self.get_extra_pse_parameters(),
                "type": "AUTHORIZATION_AND_CAPTURE",
                "paymentMethod": "PSE",
                "paymentCountry": "CO",
                "ipAddress": self.get_client_ip(self.request),
                "cookie": self.get_cookie(),
                "userAgent": self.get_user_agent(),
            },
            "test": settings.PAYU_TEST
        }

    def validate_pse_payment_data(self):
        pse_post_data = self.request.data.get('buyer_pse_data')
        pse_post_data.update(self.request.data.get('buyer'))
        serializer = PaymentsPSEDataSerializer(data=pse_post_data)
        serializer.is_valid(raise_exception=True)

    def pse_payu_payment(self):
        self.validate_pse_payment_data()
        payu_data = json.dumps(self.get_payu_pse_data())
        result = post(url=settings.PAYU_URL, data=payu_data, headers=self.headers)
        result = result.json()
        return self.pse_response(result)

    @staticmethod
    def get_bank_list_payu_data():
        return {
            "language": "es",
            "command": "GET_BANKS_LIST",
            "merchant": {
                "apiLogin": settings.PAYU_API_LOGIN,
                "apiKey": settings.PAYU_API_KEY,
            },
            "bankListInformation": {
                "paymentMethod": "PSE",
                "paymentCountry": "CO"
            },
            "test": settings.PAYU_TEST,

        }

    @staticmethod
    def bank_list_response(result):
        try:
            result = result.json()
            return result['banks']
        except:
            raise ServiceUnavailable

    def get_bank_list(self):
        payu_data = json.dumps(self.get_bank_list_payu_data())
        result = post(url=settings.PAYU_URL, data=payu_data,
                      headers={'content-type': 'application/json', 'accept': 'application/json'})
        return self.bank_list_response(result)
