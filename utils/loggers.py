import logging
from datetime import datetime
from raven.contrib.django.models import get_client

class PaymentLogger(object):
    logger = None
    client = None

    def __init__(self):
        self.client = get_client()
        self.logger = logging.getLogger('payment')

    def log_transaction(self, message, log_data):
        request = log_data.get('request')
        log_data.update({
            'request': log_data.get('request').__dict__,
        })
        self.client.user_context({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        })
        message = "{}-{}".format(message, datetime.now())
        self.logger.info(message, exc_info=True, extra=log_data)


    def log_payu_response(self, message, user, data, request):

        log_data = data.copy()
        log_data.update({
            'request': request.__dict__,
        })

        self.client.user_context({
            'id': user.id,
            'email': user.email,
            'username': user.username,
        })
        message = "{}-{}".format(message, datetime.now())
        self.logger.info(message, exc_info=True, extra=log_data)


class BalanceLogger(object):

    def __init__(self):
        self.client = get_client()
        self.logger = logging.getLogger('balance')

    def log_balance(self, organizer):
        log_data = {
            'organizer': {
                'id': organizer.id,
                'name': organizer.name,
            },
            'balance': {
                'available': {
                    'ids': organizer.balance_logs.filter(status='available') \
                                                 .values_list('id', flat=True),
                    'total': organizer.balance.available,
                },
                'unavailable': {
                    'ids': organizer.balance_logs.filter(status='unavailable') \
                                                 .values_list('id', flat=True),
                    'total': organizer.balance.unavailable,
                }
            }
        }

        self.logger.info('Balance de Organizer', exc_info=True, extra=log_data)
