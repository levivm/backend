from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response

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
