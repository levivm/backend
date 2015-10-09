from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.response import Response
from referrals.models import Coupon

from referrals.permissions import IsStudent
from referrals.tasks import SendReferralEmailTask
from students.models import Student
from students.serializer import StudentsSerializer


class InviteView(GenericAPIView):
    permission_classes = (IsStudent,)

    def get_object(self):
        return self.request.user.student_profile

    def get(self, request, *args, **kwargs):
        student = self.get_object()
        data = {
            'invite_url': student.get_referral_url(),
        }
        return Response(data)

    def post(self, request, *args, **kwargs):
        student = self.get_object()
        emails = request.data.get('emails').split(',')
        task = SendReferralEmailTask()
        task.delay(student.id, emails=emails)
        return Response('OK')


class AcceptInvitation(GenericAPIView):
    serializer_class = StudentsSerializer

    def get_object(self):
        return get_object_or_404(Student, referrer_code=self.kwargs.get('referrer_code'))

    def get(self, request, *args, **kwargs):
        student = self.get_object()
        serializer = self.get_serializer(student)
        data = serializer.data
        data.update({'refhash': student.get_referral_hash()})
        return Response(data)


class GetCouponView(RetrieveAPIView):
    permission_classes = (IsStudent,)

    def dispatch(self, request, *args, **kwargs):
        # TODO check url
        self.coupon = self.get_coupon(request.GET.get('coupon_code'))
        return super(GetCouponView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get_coupon(code):
        return get_object_or_404(Coupon, token=code)

    def retrieve(self, request, *args, **kwargs):
        if self.coupon:
            if self.coupon.is_valid(student=request.user.student_profile):
                    return Response('OK')

        return Response('Coupon invalid', status=status.HTTP_400_BAD_REQUEST)
