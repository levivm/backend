from celery import group
from django.core import signing
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from referrals.models import Referral
from referrals.tasks import CreateReferralCouponTask, CreateReferralTask
from students.models import Student


class ReferralMixin(APIView):
    """
    Mixin to resolve the referrals
    """

    is_sign_up = False
    referrer = None
    ip_address = None
    headers = None

    def dispatch(self, request, *args, **kwargs):
        self.referrer = self.get_referrer(request=request)
        self.ip_address = self.get_client_ip(request)

        if self.referrer and Referral.objects.filter(ip_address=self.ip_address).count() > 2:
            response = Response(_('No puede registrar un invitación más de dos veces desde la misma IP.'),
                                status=status.HTTP_400_BAD_REQUEST)
            self.headers = self.default_response_headers
            return self.finalize_response(request, response, *args, **kwargs)

        return super(ReferralMixin, self).dispatch(request, *args, **kwargs)

    def post(self, data, request, *args, **kwargs):
        """ Handler to call the referral creation and return the response """

        referred_id = data['user']['id']

        if self.referrer and (self.referrer.id != referred_id):
            create_referral_task = CreateReferralTask()
            create_coupons_task = CreateReferralCouponTask()
            group(
                create_referral_task.s(self.referrer.id, referred_id, self.ip_address),
                create_coupons_task.s(self.referrer.id, referred_id)
            )()
        return Response(data)

    @staticmethod
    def get_referrer(request):
        """Get a valid referrer code"""

        refhash = request.COOKIES.get('refhash')
        if refhash:
            result = signing.loads(refhash)
            try:
                student = Student.objects.get(referrer_code=result['referrer_code'])
                return student
            except Student.DoesNotExist:
                pass

    @staticmethod
    def get_client_ip(request):
        """Method to get the client ip"""

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
