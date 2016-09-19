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
