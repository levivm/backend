from celery import Task

from referrals.models import Referral, CouponType, Coupon, Redeem
from students.models import Student
from utils.tasks import SendEmailTaskMixin


class SendReferralEmailTask(SendEmailTaskMixin):
    def run(self, student_id, **kwargs):
        self.student = Student.objects.get(id=student_id)
        self.kwargs = kwargs
        template = "referrals/email/referral_cc"
        return super(SendReferralEmailTask, self).run(instance=self.student, template=template, **kwargs)

    def get_emails_to(self, *args, **kwargs):
        return self.kwargs.get('emails')

    def get_context_data(self, data):
        return {
            'name': self.student.user.first_name,
            'invite_url': self.student.get_referral_url()
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

class CreateReferralCouponTask(Task):
    """ Task to create a coupon and its relation with the student """

    def run(self, referrer_id, referred_id, *args, **kwargs):
        # Students
        referrer = Student.objects.get(id=referrer_id)
        referred = Student.objects.get(id=referred_id)

        # Coupons
        referrer_type = CouponType.objects.get(name='referrer')
        referred_type = CouponType.objects.get(name='referred')

        self.create_redeem(student=referrer, coupon_type=referrer_type)
        self.create_redeem(student=referred, coupon_type=referred_type)

    @staticmethod
    def create_redeem(student, coupon_type):
        coupon, created = Coupon.objects.get_or_create(coupon_type=coupon_type)
        redeem, created = Redeem.objects.get_or_create(student=student, coupon=coupon)

        return redeem
