from celery import Task
from django.conf import settings

from orders.models import Order

from referrals.models import Referral, CouponType, Coupon, Redeem
from students.models import Student
from utils.tasks import SendEmailTaskMixin


class SendReferralEmailTask(SendEmailTaskMixin):
    student = None
    kwargs = None

    def run(self, student_id, *args, **kwargs):
        self.student = Student.objects.get(id=student_id)
        self.template_name = "referrals/email/coupon_invitation.html"
        self.emails = kwargs.get('emails')
        self.subject = '%s te ha invitado a Trulii' % self.student.user.first_name
        self.global_context = self.get_context_data()
        return super(SendReferralEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        amount = CouponType.objects.get(name='referred').amount
        return {
            'student': {
                'name': self.student.user.get_full_name(),
                'avatar': self.student.get_photo_url(),
            },
            'amount': amount,
            'url': '%sinvitation/%s' % (settings.FRONT_SERVER_URL,
                                        self.student.referrer_code)
        }


class CreateReferralTask(Task):
    """ Task to create the relation between referred and referrer """

    def run(self, referrer_id, referred_id, ip_address, *args, **kwargs):
        referrer = Student.objects.get(id=referrer_id)
        referred = Student.objects.get(id=referred_id)

        self.create_referral(referrer=referrer, referred=referred, ip_address=ip_address)

    @staticmethod
    def create_referral(referrer, referred, ip_address):
        referral, created = Referral.objects.get_or_create(
            referrer=referrer,
            referred=referred,
            defaults={'ip_address': ip_address},
        )

        return referral


class CreateCouponTask(Task):
    """ Task to create a coupon and its relation with the student """

    def run(self, student_id, coupon_type_name, *args, **kwargs):
        student = Student.objects.get(id=student_id)
        coupon_type = CouponType.objects.get(name=coupon_type_name)

        coupon, _ = Coupon.objects.get_or_create(coupon_type=coupon_type)
        redeem, created = Redeem.objects.get_or_create(student=student, coupon=coupon)
        if created:
            task = SendCouponEmailTask()
            task.delay(redeem_id=redeem.id)

        return redeem


class ReferrerCouponTask(Task):
    """
    Task to create a referrer coupon if it's need it
    """

    def run(self, student_id, order_id, *args, **kwargs):
        student = Student.objects.get(id=student_id)
        order = Order.objects.get(id=order_id)

        if self.has_create(student, order):
            referral = Referral.objects.get(referred=student)
            task = CreateCouponTask()
            task.apply((referral.referrer.id, 'referrer'))

    @staticmethod
    def has_create(student, order):
        first_activity = student.orders.exclude(id=order.id).exclude(calendar__is_free=True).count() == 0
        is_pay_activity = order.calendar.is_free is False
        is_referred = Referral.objects.filter(referred=student).exists()
        is_approved = order.status == Order.ORDER_APPROVED_STATUS

        return first_activity and is_pay_activity and is_referred and is_approved


class SendCouponEmailTask(SendEmailTaskMixin):
    """
    Task to send the email with the coupon code to a student
    """

    def run(self, redeem_id, *args, **kwargs):
        self.redeem = Redeem.objects.get(id=redeem_id)
        self.template_name = 'referrals/email/coupon_cc_message.txt'
        self.emails = [self.redeem.student.user.email]
        self.subject = 'Tienes un cupón en Trulii!'
        self.global_context = self.get_context_data()
        return super(SendCouponEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'name': self.redeem.student.user.first_name,
            'coupon_code': self.redeem.coupon.token,
        }
