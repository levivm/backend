import mock
from django.conf import settings
from django.template import loader
from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.models import Calendar
from orders.models import Order
from referrals.models import Referral, Coupon, CouponType, Redeem
from referrals.tasks import CreateReferralTask, CreateCouponTask, ReferrerCouponTask, SendCouponEmailTask, \
    SendReferralEmailTask
from students.models import Student
from utils.models import EmailTaskRecord
from utils.tests import BaseAPITestCase


class CreateReferralTaskTest(BaseAPITestCase):
    """
    Class to test the CreateReferralTask
    """

    def setUp(self):
        super(CreateReferralTaskTest, self).setUp()

        self.ip_address = '192.0.1.12'

    def test_create(self):
        """
        Test create the instance
        """

        # Counter
        referral_counter = Referral.objects.count()

        # Call the task
        task = CreateReferralTask()
        task.delay(self.student.id, self.another_student.id, self.ip_address)

        self.assertEqual(Referral.objects.count(), referral_counter + 1)
        self.assertTrue(Referral.objects.filter(referrer=self.student, referred=self.another_student,
                                                ip_address=self.ip_address).exists())

    def test_duplicate(self):
        """
        Test should not duplicated the referral
        """

        mommy.make(Referral, referrer=self.student, referred=self.another_student)

        # Counter
        referral_counter = Referral.objects.count()

        # Call the task
        task = CreateReferralTask()
        task.delay(self.student.id, self.another_student.id, self.ip_address)

        self.assertEqual(Referral.objects.count(), referral_counter)


class CreateCouponTaskTest(BaseAPITestCase):
    """
    Class to test CreateReferralCouponTask
    """

    def setUp(self):
        super(CreateCouponTaskTest, self).setUp()

        # Coupons
        self.referrer_type = mommy.make(CouponType, name='referrer')
        self.referred_type = mommy.make(CouponType, name='referred')

    @mock.patch('referrals.tasks.SendCouponEmailTask.delay')
    def test_create(self, delay):
        """
        Test to create the coupons
        """

        coupon_counter = Coupon.objects.count()
        redeem_counter = Coupon.objects.count()

        # Call the task
        task = CreateCouponTask()
        task.delay(student_id=self.student.id, coupon_type_name='referrer')

        self.assertEqual(Coupon.objects.count(), coupon_counter + 1)
        self.assertEqual(Redeem.objects.count(), redeem_counter + 1)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.referrer_type).exists())

    def test_duplicate(self):
        """
        Test should not duplicate the coupons
        """

        mommy.make(Redeem, student=self.student, coupon__coupon_type=self.referred_type)

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = CreateCouponTask()
        task.delay(student_id=self.student.id, coupon_type_name=self.referred_type.name)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)


class ReferrerCouponTaskTest(BaseAPITestCase):
    """
    Class to test ReferrerCouponTask
    """

    def setUp(self):
        super(ReferrerCouponTaskTest, self).setUp()

        # Arrangement
        self.referral = mommy.make(Referral, referrer=self.student, referred=self.another_student)
        self.calendar = mommy.make(Calendar, activity__published=True, available_capacity=10)
        self.coupon_type = mommy.make(CouponType, name='referrer')
        self.order = mommy.make(Order, student=self.another_student, status=Order.ORDER_APPROVED_STATUS,
                                calendar=self.calendar)

    @mock.patch('referrals.tasks.SendCouponEmailTask.delay')
    def test_create(self, delay):
        """
        Test create a referrer coupon
        """

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = ReferrerCouponTask()
        task.delay(student_id=self.another_student.id, order_id=self.order.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter + 1)
        self.assertEqual(Redeem.objects.count(), redeem_counter + 1)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())

    def test_with_an_payed_activity(self):
        """
        Test case when shouldn't create a referrer coupon
        because the student already has a payed activity
        """

        # Arrangement
        mommy.make(Order, student=self.another_student)

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = ReferrerCouponTask()
        task.delay(student_id=self.another_student.id, order_id=self.order.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())

    @mock.patch('referrals.tasks.SendCouponEmailTask.delay')
    def test_having_an_free_activity(self, delay):
        """
        Test case should create the coupon
        because the student has a free activity
        """

        # Arrangement
        mommy.make(Order, student=self.another_student, calendar__is_free=True)

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = ReferrerCouponTask()
        task.delay(student_id=self.another_student.id, order_id=self.order.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter + 1)
        self.assertTrue(Coupon.objects.filter(coupon_type=self.coupon_type).exists())
        self.assertEqual(Redeem.objects.count(), redeem_counter + 1)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())

    def test_enrolling_to_a_free_activity(self):
        """
        Test case shouldn't create a coupon
        because is a free activity
        """

        # Arrangement
        self.calendar.is_free = True
        self.calendar.save(update_fields=['is_free'])

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = ReferrerCouponTask()
        task.delay(student_id=self.another_student.id, order_id=self.order.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())

    def test_without_referral(self):
        """
        Test shouldn't create the coupon because it doesn't have a referral
        """

        # Arrangement
        self.referral.delete()

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = ReferrerCouponTask()
        task.delay(student_id=self.another_student.id, order_id=self.order.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())

    def test_with_declined_order(self):
        """
        Test shouldn't create the coupon because the order was declined
        """

        # Arrangement
        self.order.status = Order.ORDER_DECLINED_STATUS
        self.order.save(update_fields=['status'])

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = ReferrerCouponTask()
        task.delay(student_id=self.another_student.id, order_id=self.order.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())

    def test_with_pending_order(self):
        """
        Test should't create the coupon because the order isn't approved yet
        """

        # Arrangement
        self.calendar.is_free = True
        self.calendar.save(update_fields=['is_free'])

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = ReferrerCouponTask()
        task.delay(student_id=self.another_student.id, order_id=self.order.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())


class SendCouponEmailTaskTest(APITestCase):
    """
    Class for testing the SendCouponEmailTask task
    """

    def setUp(self):
        # Arrangement
        self.redeem = mommy.make(Redeem)
        self.email = self.redeem.student.user.email

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        """
        Test that the task sends the email
        """

        send_mail.return_value = [{
            'email': self.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendCouponEmailTask()
        task_id = task.delay(redeem_id=self.redeem.id)

        context = {
            'name': self.redeem.student.user.first_name,
            'coupon_code': self.redeem.coupon.token,
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=self.email,
                status='sent',
                data=context,
                template_name='referrals/email/coupon_cc_message.txt').exists())


class SendReferralEmailTaskTest(APITestCase):
    """
    Class to test SendReferralEmailTask task
    """

    def setUp(self):
        mommy.make(CouponType, name='referred', amount=20000)
        self.student = mommy.make(Student)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_success(self, send_mail):
        """
        Test success case
        """
        emails = [mommy.generators.gen_email() for _ in range(3)]

        send_mail.return_value = [{
            'email': email,
            'status': 'sent',
            'reject_reason': None
        } for email in emails]

        task = SendReferralEmailTask()
        task_id = task.delay(self.student.id, emails=emails)

        context = {
            'student': {
                'name': self.student.user.get_full_name(),
                'avatar': self.student.get_photo_url(),
            },
            'amount': 20000,
            'url': '%sinvitation/%s' % (settings.FRONT_SERVER_URL,
                                        self.student.referrer_code)
        }

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='sent',
                data=context,
                template_name='referrals/email/coupon_invitation.html').exists())
