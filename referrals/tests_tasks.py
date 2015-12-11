import mock
from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.models import Calendar
from orders.models import Order
from referrals.models import Referral, Coupon, CouponType, Redeem
from referrals.tasks import CreateReferralTask, CreateCouponTask, ReferrerCouponTask, SendCouponEmailTask
from utils.models import EmailTaskRecord
from utils.tests import BaseAPITestCase


class CreateReferralTaskTest(BaseAPITestCase):
    """
    Class to test the CreateReferralTask
    """

    def setUp(self):
        super(CreateReferralTaskTest, self).setUp()

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

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

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

        # Coupons
        self.referrer_type = mommy.make(CouponType, name='referrer')
        self.referred_type = mommy.make(CouponType, name='referred')

    def test_create(self):
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
        task.delay(sstudent_id=self.student.id, coupon_type_name=self.referred_type.name)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)


class ReferrerCouponTaskTest(BaseAPITestCase):
    """
    Class to test ReferrerCouponTask
    """

    def setUp(self):
        super(ReferrerCouponTaskTest, self).setUp()

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

        # Arrangement
        self.referral = mommy.make(Referral, referrer=self.student, referred=self.another_student)
        self.calendar = mommy.make(Calendar, activity__published=True, capacity=10)
        self.coupon_type = mommy.make(CouponType, name='referrer')
        self.order = mommy.make(Order, student=self.another_student, status=Order.ORDER_APPROVED_STATUS,
                                calendar=self.calendar)

    def test_create(self):
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

    def test_having_an_free_activity(self):
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
        # Celery
        settings.CELERY_ALWAYS_EAGER = True

        # Arrangement
        self.redeem = mommy.make(Redeem)
        self.email = self.redeem.student.user.email

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_run(self, send_mail):
        """
        Test that the task sends the email
        """

        task = SendCouponEmailTask()
        task_id = task.delay(redeem_id=self.redeem.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=self.email, send=True).exists())

        context = {
            'name': self.email,
            'coupon_code': self.redeem.coupon.token,
        }

        send_mail.assert_called_with(
            'referrals/email/coupon_cc',
            self.email,
            context,
        )
